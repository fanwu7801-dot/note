## 手机钱包
>
> 目前市场上主流手机品牌的钱包功能，其核心的刷卡、支付和门卡模拟等接触式交互，确实都普遍基于NFC（近场通信）技术。

|手机品牌|核心NFC支付|交通卡|门禁卡模拟(解锁车卡)|
|-----|-----|-----|-----|
|Apple|APP_Pay|支持|限制较多|
|三星|Samsung pay|支持|支持(非加密卡)|
|小米|Mi Pay|支持|支持(非加密卡)|
|华为|Huawei Pay|支持|支持(非加密卡)|
|oppo|Oppo Pay|支持|支持(非加密卡)|
|魅族|Meizu Pay|支持|支持(非加密卡)|

> 对于手机厂商不同，钱包的支持度也有所不同，最主要的就是支持模拟解锁车卡的功能，并且NFC只能作为小于10厘米的距离进行通信，因此在车卡模拟解锁时，需要将钱包靠近车卡才能完成解锁。

### NFC/BLE车钥匙开发流程

__说明__ :仅用于华为开发者SDK实行流程，其他手机厂商的车钥匙开发流程可能有所不同。

1. 获取Apple/Google等开发者权限

> 根据不同的手机厂商，需要申请不同的开发者权限，例如Apple需要申请App权限需要99美元的费用/每年，安卓设备需要申请Google Play开发者权限25美元/买断。国内厂商开发者权限几乎都是免费的，例如小米、华为、oppo、魅族等。

2. Wallet kit简介
以华为的手机钱包为例，其提供了一个名为Wallet kit的开发框架，用于开发基于NFC的车钥匙应用。该框架提供了一系列的API，用于实现车钥匙的刷卡、支付和门卡模拟等功能。
Wallet Kit（钱包服务）集成了终端“芯-端-云”全栈技术的开放能力，可实现车钥匙、交通卡的凭证电子化。让用户能够轻松地将车钥匙和交通卡保存在手机中，以便在适当的时间使用。

- 场景介绍
  - 车钥匙
用户将车钥匙模拟到华为钱包后，相比传统车钥匙，使用手机作为车钥匙载体更适用于钥匙分享，蓝牙车钥匙等新业务场景。结合国内车厂的业界现状，可以快速实现手机车钥匙功能。

  - 交通卡
用户可以在手机上开通交通卡，使用手机替代原有的实体交通卡，可以在地铁或公交刷卡乘车。

#### 整体架构

![alt text](ble/image.png)

|角色|角色描述|
|----|----|
|DK(Digital key)|车钥匙的数字化表示，包含车钥匙的唯一标识符和相关的安全信息。|
|车钥匙Applet|华为提供安全通道供车厂将密钥以及车厂独有的数据写入Applet实例|
|BLE|低功耗蓝牙|
|NFC|近场通信|

#### 手机APP端注册手机钱包流程

车辆和移动终端的通信方式

- 车辆NFC模块。 使用NFC通道和终端芯片进行通信
- 车辆BLE模块。通过蓝牙通道。使用终端设备上的蓝牙钱包和设备终端的安全芯片通信。

1. WalletPass(Pass卡片能力)
参考HarmonyOS文档：此文档仅作为手机APP端实现车钥匙的绑定和使用。
<https://developer.huawei.com/consumer/cn/doc/harmonyos-references/wallet-walletpass>
实现绑定车钥匙Applet
2. 钥匙开通
![alt text](ble/image-1.png)
开发步骤：
1. 车主APP创建Wallet kit服务时注册的服务号和申请钥匙卡片时定义的唯一标识符，可以调用api接口进行检查车钥匙的开通流程。

``` java
import { common } from '@kit.AbilityKit';
import { walletPass } from '@kit.WalletKit';
import { BusinessError } from '@kit.BasicServicesKit';

@Entry
@Component
struct Index {
  private walletPassClient: walletPass.WalletPassClient = new walletPass.WalletPassClient(this.getUIContext().getHostContext() as common.UIAbilityContext);
  // 创建Wallet Kit服务时注册的服务号
  private passType: string = '';
  // 申请钥匙卡片时定义的卡券唯一标识
  private serialNumber: string = '';

  async queryPass() {
    let passStr = JSON.stringify({
      passType: this.passType,
      serialNumber: this.serialNumber
    });
    this.walletPassClient.queryPass(passStr).then((result: string) => {
      console.info(`Succeeded in querying pass, result: ${result}`);
    }).catch((err: BusinessError) => {
      console.error(`Failed to query pass, code:${err.code}, message:${err.message}`);
    })
  }

  build() {
    // your application UI
  }
}
```

2. api接口返回结果(环境未准备好/CanAddPass)调用则调用initWalletEnvironment接口初始化钱包开通车钥匙的同意协议或是登录账号等必要条件，引导用户跳转钱包App完成应用初始化
3. 车主APP调用queryPassDeviceInfo接口查询设备类型，指定目标设备标识。
4. 车主服务器预置模板后申请钥匙卡片以及JWE数据。
5. 用户主动发起开卡时，车主APP跳转钱包应用，调用addPass接口携带上述流程中生成的编码后的JWE数据，开通车钥匙到钱包。
6. 卡片激活的过程中需要和服务器的业务管理器进行交互，设备的认证（和车钥匙管理台交换证书信息）、获取请求个人化数据时的token（用于向车钥匙管理台请求Applet个人化数据）、以及最后的请求Applet个人化数据，最后写入安全芯片。
7. 实现车主服务器开发，此项主要用于和车钥匙管理台进行交互，用于管理和实现车辆终端的相关操作，例如车钥匙的认证、个人化数据的获取和写入等。
<https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/wallet-carkey-operation#section19676155018507>

#### 车控端

![alt text](ble/image-2.png)
典型的交互流程如下:

通过queryICCEConnectionState接口检查车控蓝牙的连接状态，如果未连接则使用startICCEConnection主动连接。
通过registerICCEListener注册监听，接收华为钱包发送的消息。
车主APP可以通过sendICCERKEMessage接口发送车控指令。
用户退出数字钥匙车控页面，通过unregisterICCEListener接口取消监听。

开发流程：

1. 调用接口，主要用于使用和创建Wallet kit服务注册时候的服务号和申请手机钥匙卡片的唯一标识，并且调用状态api`queryICCEConnectionstate`判断蓝牙钥匙的连接状态
2. 如果接口并未配对，调用api`startICCEConnction`主动创建蓝牙连接。
3. 车主app端口调用`registerICCEListener`注册监听，接收华为钱包发送的消息。
4. 车主app端口调用`sendICCERKEMessage`接口发送车控指令。
5. 用户退出数字钥匙车控页面，车主APP通过`unregisterICCEListener`接口取消监听。

### CCC、ICCE和ICCOA数字钥匙协议

1. CCC
CCC（Car Connectivity Consortium）车联网联盟是一个致力于制定智能手机到汽车连接解决方案标准的全球跨行业组织。2021年7月CCC将UWB定义为第三代数字钥匙的核心技术，并发布CCC R3（第三代数字钥匙）规范。

CCC R3是基于NFC/BLE/UWB作为基础的无线电技术的使用，该系统采用非对称密码技术对车辆和设备进行相互签名认证，且只对已知车辆显示身份，只有使用和车辆存储的公钥相对应的私钥签名计算，车辆才能进行解闭锁、启动发动机等功能。R3可以兼容R2（第二代数字钥匙），R1（第一代数字钥匙）是独立于R2、R3进行部署。

2. ICCE
ICCE（Intelligent Car Connectivity Industry Ecosystem Alliance）智慧车联产业生态联盟
ICCE是中国智能终端和汽车领域主流厂商（由华为主导）联合打造的开放平台，经过将近3年多的发展，已经成为国内车联产业领域最大的产业联盟。联盟已经构建了车钥匙、手机-车互联两大技术标准体系，并发布了8篇技术标准。到目前为止，已经有12家整车企业、共20多款车型商用或即将商用ICCE数字车钥匙，基于ICCE开放手机-车机互联标准的车型已经达到350款以上。

ICCE使用对称密钥体系

ICCE的数字钥匙是无需额外的实体钥匙，将车钥匙功能集成在移动终端设备中，基于SE，TEE等安全功能，使用NFC、蓝牙、UWB等技术连接手机和车，实现车辆开门、启动等功能。ICCE数字钥匙规范定义的，数字钥匙是在移动设备中的，但是因为规范支持手机NFC+SE的认证方案，所以如果主机厂采用卡片形式的数字钥匙，直接找个卡商开发符合规范的JavaCard Applet，直接发行卡片数字车钥匙，也是可行的，而且可能是最简单，成本最低的钥匙方案。

#### 框图讲解

![系统框图](ble/image-3.png)
ICCE数字车钥匙也定义了三个主要的实体，分别为：钥匙端、车端，后台服务，不同的是CCC数字钥匙的规范不定义车端部分，而ICCE的规范里定义了车端的实现，也可以看出来车端密钥管理是需要SE或者HSM的，而后续车端认证协议规范给出的推荐是智能卡的APDU指令，所以ICCE规范基本上明确了车端的密钥管理也是需要使用智能卡芯片的SE的。
钥匙端
钥匙端是数字钥匙的硬件实体，需要支持短距离通信（NFC、BLE、UWB、星闪至少一种）来实现数字车钥匙，在ICCE的规范中钥匙端被称作“移动终端”，但按照规范具体要求看，“移动终端”并不一定必须是手机、可穿戴设备或者实体钥匙这样的形态，所以一张符合ISO14443非接触通信协议的智能卡形态数字钥匙也是没问题的。ICCE数字车钥匙规范也支持钥匙端可以具备生物识别模块，用于实现车钥匙认证，所以如果纯卡片形态的带指纹模组的智能卡产品也是可以满足这个需求的。

1. ___Native App___
手机出厂自带的App，一般负责提供SE全局密钥管理，提供查询的界面，负责和手机厂商的TSM平台对接，负责手机SE内JavaCard Applet的空中发卡。常见的安卓手机系统中自带的钱包App就相当于这里的Native App。

2. ___业务App___
负责提供钥匙管理，查询界面，与OEM后台交互，执行开通、更新、分享、撤销等业务，在钥匙开通阶段执行蓝牙/UWB/星闪配对，负责通过车钥匙系统框架层向SE内JavaCard Applet发送APDU指令。

车钥匙系统框架层
封装了SE管理接口、钥匙认证相关接口，上层各种应用与SE交互，统一由框架层实现。业务App和Native App在同SE和车辆进行交互时，可以通过框架提供的接口实现，不用关心需要想SE发送什么APDU，不用关心7816协议/NFC/BLE/UWB/星闪的通信协议。

3. ___SE___
在手机和可穿戴设备上是SE形态的安全芯片，SE支持Global Platform规范，基本上就是GP和Java Card了。

4. ___车端___
CCC的数字钥匙规范是不包含车端实现的，但是国内做数字钥匙似乎都是主要指车端。车端模块如系统框架中所示，车上的车端数字钥匙认证系统，通过UWB/BLE/星闪/NFC等短距离通信模块，与手机建立连接，并认证。鉴权控制模块可以通过TSP通信模块和OBD诊断模块与OEM的TSP平台建立连接。

> 星闪技术：星闪（NearLink）是一项中国原生的新一代近距离无线连接技术，性能上全面超越BLE和NFC，在2025年已经在ICCE数字车钥匙规范中得到了推广。
>UWB技术：UWB（Ultra-Wideband）是一种超宽带无线通信技术，它可以在非常短的时间内传输大量数据。UWB技术的优势在于它的传输速率非常快，延迟非常低，这使得它非常适合用于车钥匙系统。

5. ___云端服务___
云端服务有主机厂的云平台、移动端厂商的云平台、移动服务提供商的云平台。基于手机或者可穿戴设备SE方案的数字钥匙，跟手机硬钱包开通交通一卡通，金融IC卡一样，需要通过TSM向SE芯片中空中发卡，需要跟移动端厂商合作，因此是需要能够对接到移动终端厂商的TSM服务器的；数字钥匙管理、控车、密钥管理等等则是主机厂自己的云服务；还可能会有移动服务提供商提供的车队管理服务、数据分析等服务。

##### 功能

1. ___钥匙端___
ICCE数字车钥匙规范中，对SE的要求为：具备安全存储、硬件加密、真随机数发生器等基本安全功能，SE还要支持Global Platform Card Specicification v2.2.1以上版本。

而数字车钥匙的Applet，也就是Java Card Applet。需要支持一个Applet实例，承载多个车钥匙的要求，遵循ICCE车钥匙的Applet实例应当使用统一的AID，数字钥匙的Applet应当保证不同厂商的钥匙数据相互隔离。

2. ___车端___
汽车需要有蓝牙BLE，UWB，NFC，星闪等模块，具备可新环境（如TEE，SE或者其他安全芯片），按照规范整体理解，BLE/NFC/UWB/星闪这些汽车只要支持一个就可以实现完成的数字钥匙方案，目前应该比较推荐的是BLE+UWB方案的数字钥匙，NFC数字钥匙作为备份。
车端的密钥管理应当使用的SE，TEE按照目前国内商密产品检测认证的经验看，TEE的安全强度通常是被视为软件密码模块的，使用TEE并不会被认为是使用了硬件密码模块，再结合ICCE规范后面给出的车端认证的APDU指令，ICCE数字车钥匙车端认证是基于智能卡技术实现的，所以车端采用SE可能是目前车端密钥应用的最合规方案。

3. ___云端服务器___
基本上是两大部分，一个是主机厂云服务，主要是数字钥匙的激活/开通/撤销/分享/查询请求的处理；另一个是手机厂商的云服务器，主要是TMS服务，是手机上Applet的管理，包括下载/更新/禁用/清除等。

##### 业务流程

![alt text](ble/image-4.png)

##### SE芯片

作为商用密码算法必须要使用ICCE标准规定的算法强度，ICCE标准值只规定了不低于4/AES128的算法强度，加密模式推荐CBC/CTR/GCM模式；公钥密码算法应使用不低于SM2/ECC256/RSA2048/ECDSA256强度的算法；密钥协商算法强度不应低于SM2/ECDH256;杂凑算法强度应当不低于SM3/SHA-256；TLS应使用不低于TLSv1.2以上版本。

所以在车端需要SE芯片作为算法解析和规定算法，并且SE芯片的密码算法强度，必须要符合ICCE标准的要求。

#### ICCE和CCC选择

ICCE数字车钥匙相比于CCC联盟的数字钥匙，都是用了智能卡技术，都需要开发Java Card Applet。相比于CCC联盟数字钥匙使用非对称加密算法，ICCE使用了对称加密算法进行双向认证，也没有CCC联盟数字钥匙相对比较复杂的汽车和钥匙配对，整体上ICCE比较简单，从信息安全功能角度看，ICCE更容易实现，只是规范里对部分具体实现细节没有详细说明，实际开发中可能需要主机厂、移动设备厂商、云平台厂商、卡商等各方再去协商确定。

总体上，ICCE数字钥匙方案更简单更容易实现、参与的汽车主机厂和手机厂商数量较多，生态较好，在国内更容易落地，使用上也相对简单，用户学习门槛较低，车主可能会更容易接受。
