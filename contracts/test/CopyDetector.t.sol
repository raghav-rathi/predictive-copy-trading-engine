// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/CopyDetector.sol";

contract MockERC20 is IERC20 {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "bal");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "bal");
        require(allowance[from][msg.sender] >= amount, "allow");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

/// @notice Deterministic 1:1 mock router: pulls amountIn of tokenIn from
///         the caller and mints amountIn of tokenOut. Pricing realism is
///         the fork test's job; unit tests verify detector logic only.
contract MockRouter is ISwapRouter {
    function exactInputSingle(ExactInputSingleParams calldata p)
        external
        payable
        returns (uint256)
    {
        IERC20(p.tokenIn).transferFrom(msg.sender, address(this), p.amountIn);
        MockERC20(p.tokenOut).mint(p.recipient, p.amountIn);
        return p.amountIn;
    }
}

contract CopyDetectorTest is Test {
    MockERC20 quote;
    MockERC20 tokenA;
    MockERC20 tokenB;
    MockRouter router;
    CopyDetector detector;
    address whale = address(0xWHALE);

    function setUp() public {
        quote = new MockERC20();
        tokenA = new MockERC20();
        tokenB = new MockERC20();
        router = new MockRouter();
        detector = new CopyDetector(address(quote), address(router), 1_000, 10_000);
        quote.mint(address(detector), 10_000);
        address[] memory cands = new address[](2);
        cands[0] = address(tokenA);
        cands[1] = address(tokenB);
        detector.registerWhale(whale, cands);
    }

    function test_noGrowth_revertsCheap() public {
        detector.snapshot(whale);
        vm.expectRevert(
            abi.encodeWithSelector(CopyDetector.NoGrowthDetected.selector, whale)
        );
        detector.attemptCopy(whale, 500, 1);
    }

    function test_growth_triggersCopy_andAdvancesSnapshot() public {
        detector.snapshot(whale);
        tokenB.mint(whale, 12345); // the "fill" lands: candidate B grew
        (address token, uint256 out) = detector.attemptCopy(whale, 500, 1);
        assertEq(token, address(tokenB));
        assertEq(out, 500);
        // snapshot auto-advanced: same fill must not re-trigger
        vm.expectRevert(
            abi.encodeWithSelector(CopyDetector.NoGrowthDetected.selector, whale)
        );
        detector.attemptCopy(whale, 500, 1);
    }

    function test_spendCap_enforced() public {
        detector.snapshot(whale);
        tokenA.mint(whale, 1);
        vm.expectRevert(
            abi.encodeWithSelector(CopyDetector.SpendCapExceeded.selector, 1_001, 1_000)
        );
        detector.attemptCopy(whale, 1_001, 1);
    }

    function test_staleSnapshot_reverts() public {
        detector.snapshot(whale);
        vm.roll(block.number + 301);
        tokenA.mint(whale, 1);
        vm.expectRevert(); // StaleSnapshot (selector match left to fork tests)
        detector.attemptCopy(whale, 100, 1);
    }

    function test_unregisteredWhale_reverts() public {
        vm.expectRevert(
            abi.encodeWithSelector(CopyDetector.WhaleNotRegistered.selector, address(0xBEEF))
        );
        detector.snapshot(address(0xBEEF));
    }

    function test_onlyOwner_registers() public {
        address[] memory cands = new address[](1);
        cands[0] = address(tokenA);
        vm.prank(address(0xBEEF));
        vm.expectRevert(CopyDetector.NotOwner.selector);
        detector.registerWhale(whale, cands);
    }
}
