import mitt from 'mitt';


const bus = mitt();

const busEvent = {

    // 缓存数据
    data: {
        responseDataSource: [], // 接口响应数据源枚举
        dataTypeMapping: [], // 数据类型枚
        apiAssertMapping: [], // 接口自动化断言方法映射举
        uiAssertMapping: [], // ui自动化断言方法映射
        runTimeout: 10,  // 等待执行测试的超时时间，默认10，运行时会去后端获取
        serverOsMapping: [],  // appium服务器系统类型
        phoneOsMapping: [],  // app测试执行设备系统类型
        deviceExtends: {},  // app扩展信息
        skipIfTypeMappingList: [], // 跳过类型枚举
        caseSkipIfDataSourceMapping: [], // 跳过数据源枚举 - 用例
        runEnvList: [], // 运行环境
        executeTypeList: [], // ui测试动作执行方式
        executeTypeDict: {}, // ui自动化执行类型
        uiExtractMappingList: [], // ui自动化数据提取方法映射
        findElementOptionList: [], // ui自动化的定位方式
        findElementOptionDict: {}, // ui自动化的定位方式


        // 未使用的变量
        permissions: [], // 用户的前端权限地址
        businessList: [], // 业务线列表
        businessDict: {}, // 业务线字典
        stepSkipIfDataSourceMapping: [], // 跳过数据源枚举 - 步骤

        uiTestExtractMappingDict: {}, // ui自动化数据提取方法映射

        runServerList: [], // app自动化运行服务器
        runPhoneList: [], // app自动化运行手机
        runBrowserNameDict: {}, // ui自动化运行浏览器
        keyboardKeyCodeList: [] // 模拟键盘输入code
    },

    // 事件
    drawerIsShow: 'drawerIsShow', // 打开抽屉
    drawerIsCommit: 'drawerIsCommit', // 抽屉已提交
    treeIsChoice: 'treeIsChoice', // 树选中事件
    treeIsDone: 'treeIsDone', // 树组装完成事件


    // 未使用的事件
    drawerIsOpen: 'drawerIsOpen', // 同步抽屉打开状态
    selectorChoice: 'selectorChoice', // 下拉框选中事件
    quoteCaseToStep: 'quoteCaseToStep', // 引用用例事件
    changeData: 'changeData' // 监听的数据发生了改变
}

export {bus, busEvent} ;


