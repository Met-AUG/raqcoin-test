# MakeNewKey() 参数与签名算法对应关系

## 概述

`CKey::MakeNewKey(unsigned int config_value)` 函数用于生成新的密钥对，参数 `config_value` 决定使用哪种后量子密码（PQC）签名算法。

本文档详细说明了不同参数值对应的签名算法及其特性。

---

## 配置值计算方法

```cpp
config_value = (type << 8) | subtype
```

其中：
- `type`: 算法类型（0=经典Rainbow, 1=RainbowPro系列, 2=混合算法）
- `subtype`: 子类型，表示具体的算法变体

---

## 完整配置列表

### 表格总览

| Config值 | Type | SubType | 算法名称 | 私钥大小(B) | 公钥大小(B) | 哈希大小(B) | 签名大小(B) | 说明 |
|---------|------|---------|---------|------------|------------|------------|------------|------|
| **0** | 0 | 0 | **PQC(Rainbow_SL0.8)** | 100,209 | 152,097 | 32 | 64 | 经典 Rainbow 算法 |
| **262** | 1 | 6 | **PQC(UOV_SL1)** | 70 | 43,598 | 44 | 172 | UOV 安全级别 1 |
| **265** | 1 | 9 | **PQC(UOV_SL3)** | 70 | 189,254 | 72 | 272 | UOV 安全级别 3 |
| **268** | 1 | 12 | **PQC(UOV_SL5)** | 70 | 447,014 | 96 | 356 | UOV 安全级别 5 |
| **274** | 1 | 18 | **PQC(Rainbow_SL1)** | 70 | 48,470 | 28 | 80 | Rainbow 压缩版 SL1 ⭐默认 |
| **280** | 1 | 24 | **PQC(Rainbow_SL3)** | 70 | 207,430 | 72 | 192 | Rainbow 压缩版 SL3 |
| **286** | 1 | 30 | **PQC(Rainbow_SL5)** | 70 | 604,358 | 96 | 268 | Rainbow 压缩版 SL5 |
| **513** | 2 | 1 | **PQC(Mix:Rainbow_SL5\|UOV_SL5)** | 146 | 1,051,378 | 192 | 624 | 混合算法（最高安全性） |

> **注意**: 默认配置 `DEFAULT_CONFIG = 4`，对应 `config_value = 274` (Rainbow SL1)

---

## 按算法类型分组

### 1. 经典 Rainbow 算法

#### `config_value = 0`
- **算法**: Rainbow Security Level 0.8 (RAINBOW16_32_32_32)
- **全名**: L1_RAINBOW_CLASSIC
- **特点**: 
  - 原始的 Rainbow 签名算法
  - 签名最小（64 bytes）
  - 私钥和公钥较大
- **使用场景**: 兼容旧版本

```cpp
CKey key;
key.MakeNewKey(0);  // 经典 Rainbow SL0.8
```

---

### 2. UOV (Unbalanced Oil and Vinegar) 系列

UOV 是一种基于多变量二次方程的后量子签名算法。

#### `config_value = 262` (Type=1, SubType=6)
- **算法**: UOV Security Level 1
- **全名**: L1_UOV_COMPRESSED (RAINBOW256_112_44_00)
- **特点**:
  - 私钥极小（70 bytes）
  - 公钥中等（43,598 bytes）
  - 签名 172 bytes
- **安全级别**: NIST Level 1

```cpp
CKey key;
key.MakeNewKey(262);  // UOV SL1
```

#### `config_value = 265` (Type=1, SubType=9)
- **算法**: UOV Security Level 3
- **全名**: L3_UOV_COMPRESSED (RAINBOW256_184_72_00)
- **特点**:
  - 私钥极小（70 bytes）
  - 公钥较大（189,254 bytes）
  - 签名 272 bytes
- **安全级别**: NIST Level 3

```cpp
CKey key;
key.MakeNewKey(265);  // UOV SL3
```

#### `config_value = 268` (Type=1, SubType=12)
- **算法**: UOV Security Level 5
- **全名**: L5_UOV_COMPRESSED (RAINBOW256_244_96_00)
- **特点**:
  - 私钥极小（70 bytes）
  - 公钥大（447,014 bytes）
  - 签名 356 bytes
- **安全级别**: NIST Level 5（最高）

```cpp
CKey key;
key.MakeNewKey(268);  // UOV SL5
```

---

### 3. Rainbow 压缩版系列

Rainbow 压缩版通过优化减少了密钥大小，同时保持安全性。

#### `config_value = 274` (Type=1, SubType=18) ⭐ **推荐/默认**
- **算法**: Rainbow Security Level 1
- **全名**: L1_RAINBOW_COMPRESSED (RAINBOW16_72_8_48)
- **特点**:
  - 私钥极小（70 bytes）
  - 公钥适中（48,470 bytes）
  - 签名小（80 bytes）
  - **系统默认配置**
- **安全级别**: NIST Level 1

```cpp
CKey key;
key.MakeNewKey(274);  // Rainbow SL1 (默认推荐)
```

#### `config_value = 280` (Type=1, SubType=24)
- **算法**: Rainbow Security Level 3
- **全名**: L3_RAINBOW_COMPRESSED (RAINBOW256_104_8_64)
- **特点**:
  - 私钥极小（70 bytes）
  - 公钥较大（207,430 bytes）
  - 签名 192 bytes
- **安全级别**: NIST Level 3

```cpp
CKey key;
key.MakeNewKey(280);  // Rainbow SL3
```

#### `config_value = 286` (Type=1, SubType=30)
- **算法**: Rainbow Security Level 5
- **全名**: L5_RAINBOW_COMPRESSED (RAINBOW256_148_8_96)
- **特点**:
  - 私钥极小（70 bytes）
  - 公钥很大（604,358 bytes）
  - 签名 268 bytes
- **安全级别**: NIST Level 5（最高）

```cpp
CKey key;
key.MakeNewKey(286);  // Rainbow SL5
```

---

### 4. 混合算法

#### `config_value = 513` (Type=2, SubType=1)
- **算法**: Mix (Rainbow SL5 + UOV SL5)
- **全名**: MIX_SIGN
- **特点**:
  - 结合了 Rainbow SL5 和 UOV SL5 的优势
  - 私钥小（146 bytes）
  - 公钥最大（1,051,378 bytes ≈ 1MB）
  - 签名最大（624 bytes）
  - **最高安全性**
- **安全级别**: NIST Level 5（双重保护）

```cpp
CKey key;
key.MakeNewKey(513);  // 混合算法（最高安全性）
```

---

## 按安全级别分组

### Security Level 0.8
- **config_value = 0**: Rainbow 经典版

### Security Level 1 (NIST Level 1)
- **config_value = 262**: UOV SL1
- **config_value = 274**: Rainbow SL1 ⭐ **默认推荐**

### Security Level 3 (NIST Level 3)
- **config_value = 265**: UOV SL3
- **config_value = 280**: Rainbow SL3

### Security Level 5 (NIST Level 5) - 最高安全级别
- **config_value = 268**: UOV SL5
- **config_value = 286**: Rainbow SL5
- **config_value = 513**: Mix (Rainbow SL5 + UOV SL5) 🔒 **最强**

---

## 使用示例

### 基本使用

```cpp
#include "key.h"

int main() {
    CKey key;
    
    // 使用默认配置（推荐）
    key.MakeNewKey(274);  // Rainbow SL1
    
    // 获取密钥信息
    CPubKey pubKey = key.GetPubKey();
    CPrivKey privKey = key.GetPrivKey();
    
    std::cout << "私钥大小: " << privKey.size() << " bytes" << std::endl;
    std::cout << "公钥大小: " << pubKey.vchPubKey.size() << " bytes" << std::endl;
    
    return 0;
}
```

### 根据需求选择算法

```cpp
// 追求最小签名大小
key.MakeNewKey(274);  // Rainbow SL1: 签名 80 bytes

// 追求最小私钥大小
key.MakeNewKey(262);  // UOV SL1: 私钥 70 bytes

// 追求最高安全性
key.MakeNewKey(513);  // Mix: 双重保护

// 平衡性能与安全性
key.MakeNewKey(280);  // Rainbow SL3
```

### 在交易测试中使用

```cpp
// 在 transactionTest.cpp 中
CBasicKeyStore keystore;
CKey key[4];

for (int i = 0; i < 4; i++) {
    // 可以为每个密钥使用不同的算法
    key[i].MakeNewKey(274);  // 使用 Rainbow SL1
    keystore.AddKey(key[i]);
}
```

---

## 性能与大小对比

### 私钥大小对比
| 算法 | 私钥大小 | 排名 |
|------|---------|------|
| UOV 系列 | 70 bytes | 🥇 最小 |
| Rainbow 压缩版 | 70 bytes | 🥇 最小 |
| Mix 混合 | 146 bytes | 较小 |
| 经典 Rainbow | 100,209 bytes | ❌ 最大 |

### 公钥大小对比
| 算法 | 公钥大小 | 排名 |
|------|---------|------|
| UOV SL1 | 43,598 bytes | 🥇 最小 |
| Rainbow SL1 | 48,470 bytes | 🥈 较小 |
| 经典 Rainbow | 152,097 bytes | 中等 |
| Rainbow SL3 | 207,430 bytes | 较大 |
| UOV SL5 | 447,014 bytes | 大 |
| Rainbow SL5 | 604,358 bytes | 很大 |
| Mix | 1,051,378 bytes | ❌ 最大 |

### 签名大小对比
| 算法 | 签名大小 | 排名 |
|------|---------|------|
| 经典 Rainbow | 64 bytes | 🥇 最小 |
| Rainbow SL1 | 80 bytes | 🥈 很小 |
| UOV SL1 | 172 bytes | 较小 |
| Rainbow SL3 | 192 bytes | 中等 |
| UOV SL3 | 272 bytes | 较大 |
| Rainbow SL5 | 268 bytes | 较大 |
| UOV SL5 | 356 bytes | 大 |
| Mix | 624 bytes | ❌ 最大 |

---

## 选择建议

### 推荐配置

| 使用场景 | 推荐配置 | Config值 | 理由 |
|---------|---------|---------|------|
| **常规使用** | Rainbow SL1 | 274 | 默认配置，平衡性好 |
| **高安全性需求** | Rainbow SL5 | 286 | NIST Level 5 |
| **极致安全** | Mix | 513 | 双重算法保护 |
| **小签名优先** | Rainbow SL1 | 274 | 签名仅 80 bytes |
| **小私钥优先** | UOV SL1 或 Rainbow SL1 | 262 或 274 | 私钥仅 70 bytes |
| **兼容旧版** | 经典 Rainbow | 0 | 向后兼容 |

### 不推荐的选择

- ❌ **config_value = 0** (经典 Rainbow): 私钥和公钥太大（100KB+），除非需要兼容
- ⚠️ **config_value = 513** (Mix): 公钥超过 1MB，传输成本高

### 实际应用建议

```cpp
// 🎯 推荐：适合大多数场景
key.MakeNewKey(274);  // Rainbow SL1

// 🔒 高价值交易或长期存储
key.MakeNewKey(286);  // Rainbow SL5

// ⚡ 需要快速验证的场景
key.MakeNewKey(274);  // Rainbow SL1 (签名小，验证快)
```

---

## 技术细节

### config_value 的结构

```
config_value (32位整数)
├─ 高8位: type (算法类型)
│   ├─ 0: 经典 Rainbow
│   ├─ 1: RainbowPro 系列（UOV/Rainbow 压缩版）
│   └─ 2: 混合算法
└─ 低8位: subtype (具体变体)
    └─ 见 SIGN_CONFIG_RBOW 数组

示例：274 = 0x0112 = (1 << 8) | 18
      ↑    ↑  ↑
      十   type=1 (RainbowPro)
      进   subtype=18 (Rainbow SL1 压缩版)
      制
```

### PUBLIC_CONFIG 数组

系统中启用的配置定义在 `PUBLIC_CONFIG` 数组中：

```c
unsigned int PUBLIC_CONFIG[PUBLIC_CONFIG_NUM+1][2] = {
    {0, 0},    // 索引0: 占位
    {1, 6},    // 索引1: UOV SL1
    {1, 9},    // 索引2: UOV SL3
    {1, 12},   // 索引3: UOV SL5
    {1, 18},   // 索引4: Rainbow SL1 (默认)
    {1, 24},   // 索引5: Rainbow SL3
    {1, 30},   // 索引6: Rainbow SL5
    {2, 1},    // 索引7: Mix
};
```

`DEFAULT_CONFIG = 4` 对应数组索引4，即 Rainbow SL1。

---

## 代码参考

### MakeNewKey 函数实现

```cpp
void CKey::MakeNewKey(unsigned int config_value)
{
    int status;
    if (0 == config_value) {
        // 使用经典 Rainbow
        privKey.resize(RAINBOW_PRIVATE_KEY_SIZE);
        pubKey.vchPubKey.resize(RAINBOW_PUBLIC_KEY_SIZE);
        status = crypto_sign_keypair(pubKey.vchPubKey.data(), privKey.data());
        if (status != 0) {
            throw key_error("CKey::MakeNewKey, make key pair failure.");
        }
    } else {
        // 使用 RainbowPlus 系列
        if (1 != rainbowplus_if_the_choised_configvalue(config_value)) {
            throw key_error("CKey::MakeNewKey, config_value not supported.");
        }
        // ... 生成密钥对
    }
    fSet = true;
}
```

### 验证签名

```cpp
bool CPubKey::Verify(unsigned int config_value, 
                     unsigned char* hash_buf, unsigned int hash_size,
                     unsigned char* sign_buf, unsigned int sign_size, 
                     bool bMsg)
{
    if (0 == config_value) {
        // 验证经典 Rainbow 签名
        int status = rainbow_verify(hash_buf, sign_buf, vchPubKey.data());
        return (0 == status);
    } else if (bMsg || nBestHeight >= RAINBOWFORkHEIGHT) {
        // 验证 RainbowPlus 签名
        // ...
    }
    return false;
}
```

---

## 常见问题

### Q1: 为什么不同算法的私钥大小差异这么大？

**A:** 经典 Rainbow (config_value=0) 使用的是原始的 Rainbow 实现，私钥需要存储大量矩阵数据（100KB+）。而 RainbowPlus 系列采用了种子生成技术，只需存储种子（70 bytes），密钥可以从种子重新生成。

### Q2: config_value = 274 为什么是默认配置？

**A:** Rainbow SL1 (config_value=274) 提供了最佳的平衡：
- 私钥小（70 bytes）
- 签名小（80 bytes）
- 公钥适中（48KB）
- 满足 NIST Level 1 安全要求
- 性能好，适合区块链应用

### Q3: 什么时候应该使用 Mix 算法？

**A:** Mix 算法 (config_value=513) 适合以下场景：
- 极高价值资产保护
- 需要防御未来量子攻击
- 对公钥大小不敏感的应用
- 需要双重算法保护的场景

但注意：公钥超过 1MB，网络传输成本高。

### Q4: 如何选择安全级别？

**A:** 安全级别选择指南：
- **Level 1**: 普通交易、日常使用
- **Level 3**: 重要交易、企业应用
- **Level 5**: 高价值资产、长期存储

### Q5: 不同算法之间可以互操作吗？

**A:** 不可以。每个 config_value 对应独立的密码系统，生成的密钥和签名格式不同，不能混用。签名验证时必须使用相同的 config_value。

---

## 更新日志

- **2025-11-07**: 初始版本，记录所有可用的签名算法配置

---

## 参考资料

- 源码文件: `src/key.cpp`, `src/key.h`
- 配置定义: `src/librainbowpro/src/rainbow/core/rb_core_rainbow-sign.c`
- Rainbow 算法: NIST PQC 标准化项目
- UOV 算法: Unbalanced Oil and Vinegar 多变量签名方案

---

## 总结

| **快速参考** | **Config值** |
|-------------|-------------|
| 默认推荐 ⭐ | 274 (Rainbow SL1) |
| 最小签名 | 274 (Rainbow SL1, 80 bytes) |
| 最小私钥 | 262/274/265/268/280/286 (70 bytes) |
| 最小公钥 | 262 (UOV SL1, 43.6 KB) |
| 最高安全 🔒 | 513 (Mix, NIST Level 5×2) |
| 兼容旧版 | 0 (经典 Rainbow) |

**建议**: 除非有特殊需求，使用默认配置 `MakeNewKey(274)` 即可。
