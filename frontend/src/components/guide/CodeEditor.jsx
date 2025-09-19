import React from 'react';

const CodeEditor = ({ code, setCode, language }) => {
  const getPlaceholder = () => {
    const placeholders = {
      python: `# Python 코드를 입력하세요
def solution():
    # 여기에 코드를 작성하세요
    pass

solution()`,
      java: `// Java 코드를 입력하세요
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        // 여기에 코드를 작성하세요
        sc.close();
    }
}`,
      cpp: `// C++ 코드를 입력하세요
#include <iostream>
using namespace std;

int main() {
    // 여기에 코드를 작성하세요
    return 0;
}`,
      javascript: `// JavaScript 코드를 입력하세요
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (line) => {
    // 여기에 코드를 작성하세요
    rl.close();
});`
    };
    
    return placeholders[language] || "여기에 코드를 입력하세요...";
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">코드 입력</label>
      <div className="relative">
        <textarea 
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder={getPlaceholder()}
          rows="15" 
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm resize-none"
        />
        {language && (
          <div className="absolute top-2 right-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
            {language.toUpperCase()}
          </div>
        )}
      </div>
      <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
        <span>줄 수: {code.split('\n').length}</span>
        <span>문자 수: {code.length}</span>
      </div>
    </div>
  );
};

export default CodeEditor;