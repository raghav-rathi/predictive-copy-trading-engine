// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Minimal ERC20 surface. Local interface so the scaffold has no
///         dependency tree to audit before the router wiring is verified.
interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @notice Minimal Uniswap-V3-style swap router surface.
///
/// TODO-verify-on-chain: Robinhood Chain (chain ID 4663) runs Uniswap
/// v2/v3/v4, and fills in our research touched the v4 PoolManager via a
/// Universal Router. The exact router address, and whether v3
/// SwapRouter02-style `exactInputSingle` or v4 Universal Router
/// `execute` is the right entry point, must be confirmed against the
/// live chain before deployment. No address is hardcoded here on
/// purpose; the router is a constructor argument.
interface ISwapRouter {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params)
        external
        payable
        returns (uint256 amountOut);
}

/// @title CopyDetector
/// @notice Same-block copy detector for Robinhood Chain.
///
/// The trick from @outputlayer's "Predictive Copy Trading on Robinhood
/// Chain" (see docs/research): watch the Solana leg of the FOMO app and
/// you learn *who* is about to buy 0.5-1.6s (~5-16 blocks) before the
/// fill lands -- but never *what*. So don't predict the token; test for
/// it at execution time:
///
///   1. `snapshot(whale)` records the whale's balances of a candidate
///      token set (maintained off-chain by the scorer; per-whale token
///      history is the current source of candidates).
///   2. During the fill window, authorized callers stream
///      `attemptCopy(whale, ...)` calls, a few per block.
///   3. Each call diffs the whale's live candidate balances against the
///      snapshot. Nothing grew -> revert `NoGrowthDetected` (~31k gas,
///      cents): a cheap miss. Something grew -> that is the token the
///      whale just received; swap into it in the same block.
///
/// After a successful copy the snapshot for that token auto-advances to
/// the whale's current balance, so one fill cannot re-trigger the burst.
///
/// What is verified vs TODO:
///   - The balance-diff/same-block behavior matches the mechanism
///     observed on-chain (operator buys land in the fill's block).
///   - Router address, pool fee tier per pair, and the candidate-set
///     source are deployment-time values: TODO-verify-on-chain.
///   - Only wallets the scorer classifies COPY should be registered.
///     This contract enforces size/slippage caps; classification lives
///     off-chain in scorer/wallet_scorer.py.
contract CopyDetector {
    error NotOwner();
    error NotCaller();
    error WhaleNotRegistered(address whale);
    error NoGrowthDetected(address whale);
    error StaleSnapshot(address whale, uint256 snapshotBlock, uint256 currentBlock);
    error SpendCapExceeded(uint256 requested, uint256 cap);
    error SlippageExceeded(uint256 amountOut, uint256 minOut);
    error NoCandidates(address whale);
    error TooManyCandidates(uint256 count);

    event WhaleRegistered(address indexed whale, uint256 candidateCount);
    event WhaleRemoved(address indexed whale);
    event SnapshotTaken(address indexed whale, uint256 blockNumber, uint256 candidateCount);
    event CopyExecuted(
        address indexed whale, address indexed token, uint256 amountIn, uint256 amountOut
    );

    uint256 public constant MAX_CANDIDATES = 24;

    address public owner;
    /// @notice Quote asset spent on copies (USDG on Robinhood Chain).
    ///         Set at deployment after on-chain verification.
    IERC20 public immutable quoteToken;
    ISwapRouter public immutable swapRouter;
    /// @notice Hard per-call spend cap, in quote-token raw units.
    uint256 public spendCapPerCall;
    /// @notice Pool fee tier used for copies (Uniswap v3 style, e.g. 10000 = 1%).
    uint24 public poolFee;
    /// @notice Snapshots older than this many blocks are refused
    ///         (~100ms blocks: 300 blocks = ~30s).
    uint256 public maxSnapshotAgeBlocks;

    mapping(address => bool) public callers;
    mapping(address => address[]) private _candidates;
    mapping(address => mapping(address => uint256)) public snapshotBalance;
    mapping(address => uint256) public snapshotBlock;

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyCaller() {
        if (!callers[msg.sender]) revert NotCaller();
        _;
    }

    constructor(address _quoteToken, address _swapRouter, uint256 _spendCapPerCall, uint24 _poolFee) {
        owner = msg.sender;
        callers[msg.sender] = true;
        quoteToken = IERC20(_quoteToken);
        swapRouter = ISwapRouter(_swapRouter);
        spendCapPerCall = _spendCapPerCall;
        poolFee = _poolFee;
        maxSnapshotAgeBlocks = 300;
    }

    // -- owner administration -------------------------------------------------

    function setCaller(address who, bool allowed) external onlyOwner {
        callers[who] = allowed;
    }

    function setSpendCap(uint256 cap) external onlyOwner {
        spendCapPerCall = cap;
    }

    function setMaxSnapshotAge(uint256 blocks_) external onlyOwner {
        maxSnapshotAgeBlocks = blocks_;
    }

    /// @notice Register (or replace) the candidate token set for a whale.
    ///         Only scorer-classified COPY wallets should ever be added.
    function registerWhale(address whale, address[] calldata candidates) external onlyOwner {
        if (candidates.length == 0) revert NoCandidates(whale);
        if (candidates.length > MAX_CANDIDATES) revert TooManyCandidates(candidates.length);
        _candidates[whale] = candidates;
        emit WhaleRegistered(whale, candidates.length);
    }

    function removeWhale(address whale) external onlyOwner {
        delete _candidates[whale];
        snapshotBlock[whale] = 0;
        emit WhaleRemoved(whale);
    }

    function candidatesOf(address whale) external view returns (address[] memory) {
        return _candidates[whale];
    }

    // -- the detector ---------------------------------------------------------

    /// @notice Record the whale's current candidate balances. Call when a
    ///         Solana-side trigger opens the fill window.
    function snapshot(address whale) external onlyCaller {
        address[] storage cands = _candidates[whale];
        if (cands.length == 0) revert WhaleNotRegistered(whale);
        for (uint256 i = 0; i < cands.length; i++) {
            snapshotBalance[whale][cands[i]] = IERC20(cands[i]).balanceOf(whale);
        }
        snapshotBlock[whale] = block.number;
        emit SnapshotTaken(whale, block.number, cands.length);
    }

    /// @notice Diff live balances vs the snapshot; on growth, swap into
    ///         the grown token. Reverts cheaply when nothing grew.
    /// @param minOut Slippage guard, computed off-chain from the pool
    ///        quote at burst time (the engine owns pricing; the contract
    ///        refuses to fill below it).
    function attemptCopy(address whale, uint256 amountIn, uint256 minOut)
        external
        onlyCaller
        returns (address token, uint256 amountOut)
    {
        address[] storage cands = _candidates[whale];
        if (cands.length == 0) revert WhaleNotRegistered(whale);
        uint256 snapAt = snapshotBlock[whale];
        if (snapAt == 0 || block.number - snapAt > maxSnapshotAgeBlocks) {
            revert StaleSnapshot(whale, snapAt, block.number);
        }
        if (amountIn > spendCapPerCall) revert SpendCapExceeded(amountIn, spendCapPerCall);

        for (uint256 i = 0; i < cands.length; i++) {
            address cand = cands[i];
            uint256 now_ = IERC20(cand).balanceOf(whale);
            if (now_ > snapshotBalance[whale][cand]) {
                // Advance the snapshot first: one fill, one copy, even if
                // the burst keeps firing for the rest of the window.
                snapshotBalance[whale][cand] = now_;
                amountOut = _swap(cand, amountIn, minOut);
                emit CopyExecuted(whale, cand, amountIn, amountOut);
                return (cand, amountOut);
            }
        }
        revert NoGrowthDetected(whale);
    }

    function _swap(address tokenOut, uint256 amountIn, uint256 minOut)
        internal
        returns (uint256 amountOut)
    {
        uint256 bal = quoteToken.balanceOf(address(this));
        uint256 spend = amountIn < bal ? amountIn : bal;
        if (spend == 0) revert SpendCapExceeded(0, spendCapPerCall);
        quoteToken.approve(address(swapRouter), spend);
        amountOut = swapRouter.exactInputSingle(
            ISwapRouter.ExactInputSingleParams({
                tokenIn: address(quoteToken),
                tokenOut: tokenOut,
                fee: poolFee,
                recipient: address(this),
                amountIn: spend,
                amountOutMinimum: minOut,
                sqrtPriceLimitX96: 0
            })
        );
        if (amountOut < minOut) revert SlippageExceeded(amountOut, minOut);
    }

    /// @notice Owner-only sweep of accumulated copy inventory / leftover
    ///         quote. Exit *policy* (when to sell) lives in the engine;
    ///         this is only the vault door.
    function sweep(address token, address to, uint256 amount) external onlyOwner {
        require(IERC20(token).transfer(to, amount), "sweep failed");
    }
}
