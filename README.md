# ⚡ ThunderJS Runtime

A custom-built **Mini JavaScript Interpreter / Runtime in Python** created for **Thunder Hackathon 2.0 — Build Your Own JavaScript**.

ThunderJS Runtime accepts JavaScript code as input, translates it into executable Python, and executes it while preserving JavaScript-like behavior.

---
# This Project Contains 2 modes :1.Web IDE 2.CLI mode 
---
## 🚀 Getting Started

### 📦 1. Clone the Repository
```bash
git clone https://github.com/krushang15THECODER/JS-runtime.git
cd JS-runtime
```

---

### 📥 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Run ThunderJS Runtime

### 📄 File Execution Mode(To run a whole file)
Run a JavaScript file using the interpreter:

```bash
python main.py test.js
```

---

### 🧪 REPL Mode (Interactive Shell)(To run argument by argument)
Start a live JavaScript terminal:

```bash
python main.py --repl
```

Example:

```bash
JS > let x = 10;
JS > console.log(x);
10
JS > exit
```

---

## 🌐 Web Version

Open in browser:

https://js-runtime-p4du.onrender.com/

Features:
- Code editor
- Run button
- Live output terminal
- No setup required

---

## ⚡ Quick Summary

| Mode | Command | Use Case |
|------|--------|----------|
| 📄 File Mode | `python main.py file.js` | Run full programs |
| 🧪 REPL Mode | `python main.py --repl` | Interactive testing |
| 🌐 Web Mode | https://js-runtime-p4du.onrender.com/ | Browser-based IDE |
```
---
# 🏗️ Architecture

ThunderJS Runtime follows a lightweight **compiler-style pipeline**:

```txt
JavaScript Code
        ↓
Parser + Translator (JS → Python)
        ↓
Runtime Engine (JS semantics layer)
        ↓
Python Execution (exec sandbox)
        ↓
Output Renderer (CLI / REPL / Web)
```
Core Files:

```txt
app.py
main.py
translator.py
runtime.py
templates/index.html
```

---
# 🎯 Project Goal

Instead of writing JavaScript, the challenge was to **build something that can run JavaScript**.

This project:

✅ Accepts JavaScript code input
✅ Parses and translates JavaScript → Python
✅ Executes translated code
✅ Produces JavaScript-like output
✅ Includes an interactive browser-based IDE

Built entirely in **Python**, without using:

❌ Node.js
❌ JavaScript as the primary language
❌ TypeScript
❌ Babel / JS transpilers

---

# ✨ Supported Features

## 📦 Variables & Data Types

### Variable Declarations

* `let`
* `const`

### Primitive Data Types

* `number`
* `string`
* `boolean`
* `null`
* `undefined`

### Non-Primitive Types

* `array`
* `object`
* `function`

### Type Coercion

* JavaScript-style string concatenation
* JS-like `+` behavior
* Type-safe equality handling

---

## ⚙️ Operators

### Arithmetic Operators

* `+`
* `-`
* `*`
* `/`
* `%`
* `**`

### Comparison Operators

* `>`
* `<`
* `>=`
* `<=`
* `===`
* `!==`

### Logical Operators

* `&&`
* `||`
* `!`

### Assignment Operators

* `=`
* `+=`
* `-=`
* `++`
* `--`

---

## 🔀 Conditional Statements

Supported:

* `if`
* `else if`
* `else`

Example:

```js
let age = 20;

if (age >= 18) {
    console.log("Adult");
} else {
    console.log("Minor");
}
```

---

## 🔁 Loops

### For Loop

```js
for (let i = 1; i <= 5; i++) {
    console.log(i);
}
```

### While Loop

```js
while (x > 0) {
    x--;
}
```

### Nested Loops

Triangle patterns and nested iteration supported.

---

# 🧠 Functions

### Function Declarations

```js
function greet() {
    console.log("Hello");
}
```

### Recursive Functions

Supported.

Example:

```js
function factorial(n) {
    if (n === 0) {
        return 1;
    }

    return n * factorial(n - 1);
}
```

### Function Expressions

Supported.

### Arrow Functions

```js
x => x * 2
(a, b) => a + b
(a, b) => a - b
```

---

# 📚 Arrays

### Array Creation

```js
let arr = [1,2,3];
```

### Supported Array Methods

✅ `push()`
✅ `pop()`
✅ `shift()`
✅ `unshift()`
✅ `slice()`
✅ `splice()`
✅ `concat()`
✅ `includes()`
✅ `indexOf()`
✅ `sort()`
✅ `reverse()`
✅ `join()`

### Comparator Sorting

Supports JavaScript comparator sorting:

```js
arr.sort((a,b)=>a-b)
arr.sort((a,b)=>b-a)
```

---

# 🧵 String Methods

Supported:

✅ `replace()`
✅ `replaceAll()`
✅ `substring()`
✅ `slice()`
✅ `split()`
✅ `trim()`
✅ `toUpperCase()`
✅ `toLowerCase()`
✅ `includes()`
✅ `startsWith()`
✅ `endsWith()`
✅ `indexOf()`

Example:

```js
let str = "racecar";

console.log(
    str.split("")
       .reverse()
       .join("")
);
```

---

# 🧩 Objects

Object creation and property access supported.

Example:

```js
let student = {
    name: "Krushang",
    age: 20
};

console.log(student.name);
console.log(student.age);
```

---

# 🧮 Callback-Based Array Methods

Supported:

✅ `map()`
✅ `filter()`
✅ `reduce()`
✅ `find()`
✅ `some()`
✅ `every()`

Example:

```js
let nums = [1,2,3];

let doubled =
    nums.map(x => x * 2);

console.log(doubled);
```

---

# 🧠 Math Object

Supported:

✅ `Math.floor()`
✅ `Math.ceil()`
✅ `Math.max()`
✅ `Math.min()`
✅ `Math.random()`

Example:

```js
console.log(Math.floor(4.9));
```

---

# 📅 Date Object

Basic `Date` support implemented.

---

# 🌪 Spread Operator

Supported:

```js
let copy = [...arr];
```
---

# 🛠️ Tech Stack

* Python
* Flask
* HTML
* CSS
* JavaScript

---

# ▶️ Run Locally

Clone repository:

```bash
git clone https://github.com/krushang15THECODER/JS-runtime.git
```

Move into project:

```bash
cd thunder-js-runtime
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
python app.py
```

Open locally:

```txt
http://127.0.0.1:5000
```

---

# 🧪 Sample JavaScript Code

```js
let num = 7;

if (num % 2 === 0) {
    console.log(num + " is Even");
} else {
    console.log(num + " is Odd");
}
```

Output:

```txt
7 is Odd
```

---

# 🏆 Hackathon

Built for:

**Thunder Hackathon 2.0 — Build Your Own JavaScript**

---

# 👨‍💻 Author

**Krushang Surati**
