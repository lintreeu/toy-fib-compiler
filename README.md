# A Simple Compiler for Fibonacci

此專案使用 Python 搭配 [llvmlite](https://github.com/numba/llvmlite) 建立一個簡易的類 C 語言編譯器用來編譯Fibonacci數列，包含：

1. **Lexer**：使用正則表達式進行詞法分析。
2. **Parser**：使用遞迴下降解析法產生抽象語法樹 (AST)。
3. **AST**：使用 Python 類別定義節點，包括變數、函式呼叫、二元運算等。
4. **CodeGen**：將 AST 轉換為 LLVM IR。
5. **JIT Execution**：透過 llvmlite 的 JIT 執行產生的 LLVM IR。

## 目錄結構

```plaintext
├── lexer.py          # 詞法分析器
├── parser.py         # 語法分析器
├── ast_nodes.py      # AST 節點定義
├── codegen.py        # AST 轉 LLVM IR 的主要邏輯
├── main.py           # 程式進入點：呼叫上述模組並執行
├── example.fib       # 測試程式碼(可自定名稱)
├── requirements.txt  # 相關套件需求
└── README.md         # 說明檔
```

## 如何使用

1. 安裝必要套件

   ```bash
   pip install -r requirements.txt
   ```
2. 放入您的自訂程式碼（類似 `example.fib`）到專案目錄下。例如以下範例程式碼：

   ```c
   def fib(n) {
       if n <= 1 {
           return n
       } else {
           return fib(n - 1) + fib(n - 2)
       }
   }

   def main() {
       return fib(10)
   }
   ```

3. 執行編譯與 JIT：

   ```bash
   python main.py example.fib
   ```

   - 將顯示以下資訊：
     1. **AST Visual**：可視化抽象語法樹。
     2. **Generated LLVM IR**：輸出 LLVM IR 程式。
     3. **Running JIT**：執行 IR，並顯示程式的返回值。

## 注意事項

- 這個範例只提供基礎範例，並未包含完整錯誤處理或所有語言特性。
- 您可以基於此專案擴充不同語法糖、更複雜的資料型別或更多運算子支援。

## License

本範例以 MIT License 授權，歡迎自由使用與修改。
