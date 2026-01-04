/**
 * 水印工具类
 * 用于在页面上添加和移除水印
 */

let watermarkDiv: HTMLElement | null = null;

class Watermark {
  /**
   * 设置水印
   * @param text 水印文字
   */
  static set(text: string) {
    this.del();
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return;
    
    canvas.width = 200;
    canvas.height = 150;
    
    ctx.rotate((-20 * Math.PI) / 180);
    ctx.font = '16px Arial';
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, canvas.width / 3, canvas.height / 2);
    
    const watermarkEl = document.createElement('div');
    watermarkEl.style.position = 'fixed';
    watermarkEl.style.top = '0';
    watermarkEl.style.left = '0';
    watermarkEl.style.width = '100%';
    watermarkEl.style.height = '100%';
    watermarkEl.style.zIndex = '9999';
    watermarkEl.style.pointerEvents = 'none';
    watermarkEl.style.backgroundImage = `url(${canvas.toDataURL('image/png')})`;
    watermarkEl.style.backgroundRepeat = 'repeat';
    watermarkEl.setAttribute('id', 'watermark');
    
    document.body.appendChild(watermarkEl);
    watermarkDiv = watermarkEl;
  }
  
  /**
   * 删除水印
   */
  static del() {
    if (watermarkDiv) {
      document.body.removeChild(watermarkDiv);
      watermarkDiv = null;
    }
    
    // 兼容处理：删除可能存在的其他水印元素
    const existingWatermark = document.getElementById('watermark');
    if (existingWatermark) {
      document.body.removeChild(existingWatermark);
    }
  }
}

export default Watermark;