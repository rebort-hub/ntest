/**
 * AI 自动化脚本生成相关工具函数
 * 临时解决方案，避免导入路径问题
 */

// 模拟API调用函数
export const generateAutomationScripts = async (data: any) => {
  // 模拟API延迟
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // 返回模拟数据
  return {
    data: {
      data: {
        success_count: data.api_ids.length,
        failed_count: 0,
        total_lines: data.api_ids.length * 50,
        generated_scripts: data.api_ids.map((id: number, index: number) => ({
          api_id: id,
          api_name: `接口${index + 1}`,
          script_content: generateMockScript(`接口${index + 1}`, data.script_type),
          script_type: data.script_type,
          script_language: data.script_language,
          file_name: `test_api_${index + 1}.${data.script_language === 'python' ? 'py' : 'java'}`
        })),
        failed_apis: []
      }
    }
  }
}

export const getLLMConfigs = async () => {
  // 模拟API延迟
  await new Promise(resolve => setTimeout(resolve, 500))
  
  return {
    data: {
      data: [
        { id: 1, name: 'OpenAI GPT-4' },
        { id: 2, name: 'OpenAI GPT-3.5' },
        { id: 3, name: 'Claude-3' }
      ]
    }
  }
}

export const importSwaggerAndGenerateScripts = async (data: any) => {
  // 模拟API延迟
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  return {
    data: {
      data: {
        message: "Swagger导入成功",
        imported_apis: 15,
        generated_scripts: data.auto_generate_script ? 15 : 0
      }
    }
  }
}

// 生成模拟脚本内容
const generateMockScript = (apiName: string, scriptType: string) => {
  if (scriptType === 'pytest') {
    return `"""
${apiName} 自动化测试脚本
自动生成时间: ${new Date().toLocaleString()}
"""
import pytest
import requests

class Test${apiName.replace(/\s+/g, '')}:
    
    def test_${apiName.toLowerCase().replace(/\s+/g, '_')}_success(self):
        """测试 ${apiName} - 正常流程"""
        url = "http://localhost:8080/api/test"
        
        response = requests.get(url)
        
        assert response.status_code == 200
        assert response.json() is not None
        
    def test_${apiName.toLowerCase().replace(/\s+/g, '_')}_invalid_params(self):
        """测试 ${apiName} - 异常参数"""
        url = "http://localhost:8080/api/test"
        
        response = requests.get(url, params={"invalid": "param"})
        
        assert response.status_code in [400, 422]
`
  } else {
    return `/**
 * ${apiName} 自动化测试脚本
 * 自动生成时间: ${new Date().toLocaleString()}
 */
package com.test.api;

import org.testng.annotations.*;
import org.testng.Assert;
import io.restassured.RestAssured;
import io.restassured.response.Response;

public class ${apiName.replace(/\s+/g, '')}Test {
    
    @Test
    public void test${apiName.replace(/\s+/g, '')}Success() {
        Response response = RestAssured
            .given()
            .when()
            .get("/api/test")
            .then()
            .extract()
            .response();
        
        Assert.assertEquals(response.getStatusCode(), 200);
        Assert.assertNotNull(response.getBody().asString());
    }
    
    @Test
    public void test${apiName.replace(/\s+/g, '')}InvalidParams() {
        Response response = RestAssured
            .given()
            .queryParam("invalid", "param")
            .when()
            .get("/api/test")
            .then()
            .extract()
            .response();
        
        Assert.assertTrue(response.getStatusCode() == 400 || response.getStatusCode() == 422);
    }
}
`
  }
}