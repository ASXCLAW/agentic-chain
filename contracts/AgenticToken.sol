// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title AgenticToken ($AGENTIC)
 * @dev The native token of Agentic Chain - Launch on Base via bankr.bot
 */
contract AgenticToken is ERC20, Ownable {
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18;
    
    // Tax configuration
    uint256 public buyTax = 200;      // 2% on buy
    uint256 public sellTax = 500;     // 5% on sell
    uint256 public transferTax = 0;   // 0% on transfer
    
    // Tax recipients
    address public taxVault;
    address public stakingReward;
    
    // Trading state
    bool public tradingEnabled = false;
    mapping(address => bool) public isExcludedFromTax;
    mapping(address => bool) public isMarketMaker;
    
    // Anti-bot
    uint256 public launchedAt;
    uint256 public launchTaxPeriod = 300 seconds;
    uint256 public maxBuyPerWallet = 1_000_000 * 10**18;
    mapping(address => uint256) public boughtAmount;
    
    // Staking
    uint256 public totalStaked;
    mapping(address => uint256) public stakedAmount;
    mapping(address => uint256) public lastStakeTime;
    uint256 public stakingRewardPool;
    
    // Events
    event TaxRateUpdated(uint256 buyTax, uint256 sellTax);
    event TradingEnabled(uint256 timestamp);
    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);
    
    constructor() ERC20("Agentic Chain", "AGENTIC") Ownable(msg.sender) {
        // Exclude deployer and contracts from tax
        isExcludedFromTax[msg.sender] = true;
        isExcludedFromTax[address(this)] = true;
        
        // Mint max supply to deployer
        _mint(msg.sender, MAX_SUPPLY);
        
        taxVault = msg.sender;
        stakingReward = msg.sender;
    }
    
    /**
     * @dev Enable trading
     */
    function enableTrading() external onlyOwner {
        require(!tradingEnabled, "Already enabled");
        tradingEnabled = true;
        launchedAt = block.timestamp;
    }
    
    /**
     * @dev Set tax rates
     */
    function setTaxRates(uint256 _buyTax, uint256 _sellTax) external onlyOwner {
        require(_buyTax <= 1000, "Max 10%");
        require(_sellTax <= 1000, "Max 10%");
        buyTax = _buyTax;
        sellTax = _sellTax;
        emit TaxRateUpdated(_buyTax, _sellTax);
    }
    
    /**
     * @dev Set tax vault
     */
    function setTaxVault(address _vault) external onlyOwner {
        require(_vault != address(0), "Invalid address");
        taxVault = _vault;
    }
    
    /**
     * @dev Override transfer with tax logic
     */
    function transfer(address to, uint256 amount) public override returns (bool) {
        return _transferWithTax(_msgSender(), to, amount);
    }
    
    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        return _transferWithTax(from, to, amount);
    }
    
    function _transferWithTax(address from, address to, uint256 amount) internal returns (bool) {
        uint256 tax = 0;
        
        if (!isExcludedFromTax[from] && !isExcludedFromTax[to]) {
            // Determine tax rate
            if (tradingEnabled) {
                // Check if buy or sell (simplified - in production use Uniswap checks)
                bool isBuy = isMarketMaker[to];
                bool isSell = isMarketMaker[from];
                
                if (isBuy) {
                    // Buy tax
                    tax = (amount * buyTax) / 10000;
                    
                    // Anti-bot: limit buy during launch
                    if (block.timestamp < launchedAt + launchTaxPeriod) {
                        require(boughtAmount[to] + tax <= maxBuyPerWallet, "Max buy limit");
                        boughtAmount[to] += (amount - tax);
                    }
                } else if (isSell) {
                    // Sell tax
                    tax = (amount * sellTax) / 10000;
                } else {
                    // Regular transfer - no tax
                    tax = 0;
                }
            }
        }
        
        uint256 amountAfterTax = amount - tax;
        
        if (tax > 0) {
            _transfer(from, taxVault, tax);
        }
        _transfer(from, to, amountAfterTax);
        
        return true;
    }
    
    /**
     * @dev Stake tokens
     */
    function stake(uint256 amount) external {
        require(amount > 0, "Cannot stake 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        
        // Claim existing rewards
        if (stakedAmount[msg.sender] > 0) {
            _claimStakingRewards();
        }
        
        _transfer(msg.sender, address(this), amount);
        stakedAmount[msg.sender] += amount;
        totalStaked += amount;
        lastStakeTime[msg.sender] = block.timestamp;
        
        emit Staked(msg.sender, amount);
    }
    
    /**
     * @dev Unstake tokens
     */
    function unstake(uint256 amount) external {
        require(amount > 0, "Cannot unstake 0");
        require(stakedAmount[msg.sender] >= amount, "Insufficient staked");
        
        // Claim rewards first
        _claimStakingRewards();
        
        stakedAmount[msg.sender] -= amount;
        totalStaked -= amount;
        _transfer(address(this), msg.sender, amount);
        
        emit Unstaked(msg.sender, amount);
    }
    
    /**
     * @dev Claim staking rewards
     */
    function claimStakingRewards() external {
        _claimStakingRewards();
    }
    
    function _claimStakingRewards() internal {
        uint256 staked = stakedAmount[msg.sender];
        if (staked == 0) return;
        
        // Calculate rewards: 12% APY
        uint256 timeStaked = block.timestamp - lastStakeTime[msg.sender];
        uint256 rewards = (staked * 12 * timeStaked) / (365 days * 100);
        
        if (rewards > 0 && stakingRewardPool >= rewards) {
            _transfer(address(this), msg.sender, rewards);
            stakingRewardPool -= rewards;
            emit RewardsClaimed(msg.sender, rewards);
        }
        
        lastStakeTime[msg.sender] = block.timestamp;
    }
    
    /**
     * @dev Add to staking reward pool
     */
    function addToRewardPool() external payable {
        // Can be funded via tax vault or direct
        stakingRewardPool += msg.value;
    }
    
    /**
     * @dev Get pending rewards
     */
    function getPendingRewards(address account) external view returns (uint256) {
        uint256 staked = stakedAmount[account];
        if (staked == 0) return 0;
        
        uint256 timeStaked = block.timestamp - lastStakeTime[account];
        return (staked * 12 * timeStaked) / (365 days * 100);
    }
    
    /**
     * @dev Exclude from tax
     */
    function setExcludedFromTax(address account, bool excluded) external onlyOwner {
        isExcludedFromTax[account] = excluded;
    }
    
    /**
     * @dev Set market maker
     */
    function setMarketMaker(address account, bool mm) external onlyOwner {
        isMarketMaker[account] = mm;
    }
    
    receive() external payable {
        stakingRewardPool += msg.value;
    }
}
