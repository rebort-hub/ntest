import { GetConfigByCode, GetFindElementBy } from '@/api/config/config-value'
import {busEvent} from "@/utils/bus-events";
import {GetAssertMappingList, GetExtractMappingList} from "@/api/autotest/step";
// import { GetAssertMapping, GetExtractMapping } from '@/api/autotest/step'
// import { assertMappingList, extractMappingList } from '@/apis/webUiTest/step'

// 获取配置的运行等待超时时间
export function getRunTimeout() {
    if (busEvent.data.runTimeout === 10){
        GetConfigByCode({ code: 'run_time_out' }).then(response => {
            busEvent.data.runTimeout = response.data
        })
    }
}

// 获取ui自动化元素定位方式
export function getFindElementOption(testType: any) {
    if (busEvent.data.findElementOptionList.length < 1){
        let findElementOption: [] = []
        GetFindElementBy({ 'test_type': testType }).then(response => {
            findElementOption = response.data
            busEvent.data.findElementOptionList = findElementOption
            // 列表解析为字典
            const optionDict = {}
            findElementOption.forEach(option => {
                optionDict[option.value] = option.label
            })
            busEvent.data.findElementOptionDict = optionDict
        })
    }
}

// // 获取ui自动化数据提取类型
// export function getExtractTypeList(_this) {
//   let tempList = []
//   extractTypeList().then(response => {
//     tempList = response.data
//     _this.$busEvents.data.extractTypeList = tempList
//     // 列表解析为字典
//     let tempDict = []
//     tempList.forEach(option => {
//       tempDict[option.value] = option.label
//     })
//     _this.$busEvents.data.extractTypeDict = tempDict
//   })
//   return tempList
// }

// 获取ui自动化数据提取类型
export function getExtractMappingList(testType: string) {
   GetExtractMappingList(testType).then(response => {
       busEvent.data.executeTypeList = response.data
       busEvent.data.executeTypeDict = {}
       busEvent.data.executeTypeList.forEach(item => {
           busEvent.data.executeTypeList[item.value] = item.label
       })
   })
}

// 获取ui自动化断言方法
export function getUiAssertMappingList(testType: string) {
    GetAssertMappingList(testType).then(response => {
        busEvent.data.uiAssertMapping = response.data
    })
}
