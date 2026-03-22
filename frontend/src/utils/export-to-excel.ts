import * as XLSX from 'xlsx';

const exportToExcel = (dataList: unknown[]) => {
    const ws = XLSX.utils.json_to_sheet(dataList);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');

    // 创建一个 Blob 对象并设置文件类型
    const wbout = XLSX.write(wb, {bookType: 'xlsx', type: 'binary'});
    const blob = new Blob([s2ab(wbout)], {type: 'application/octet-stream'});

    // 创建一个下载链接并触发下载
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data.xlsx';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }, 0);
}

const s2ab = (s: string) => {
    const buf = new ArrayBuffer(s.length);
    const view = new Uint8Array(buf);
    for (let i = 0; i < s.length; i++) {
        view[i] = s.charCodeAt(i) & 0xFF;
    }
    return buf;
}

export default exportToExcel
