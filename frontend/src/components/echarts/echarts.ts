
import * as echarts from 'echarts'

const themeName = 'macarons'
import themeJson from "./macarons.json";
// import themeJson from "./walden.json";


echarts.registerTheme(themeName, themeJson)

export {echarts, themeName}
export function getNewChart(chartRef: HTMLElement | null | undefined){
    return echarts.init(chartRef, themeName)
}
