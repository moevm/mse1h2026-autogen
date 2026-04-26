from prog_questions.spring import QuestionN3
from prog_questions import Result, utility
from utility import moodleInit
import pytest


class TestQuestionN3:
    question1 = moodleInit(QuestionN3, seed=1)

    def test_question_text_1(self):
        text = self.question1.questionText
        assert 'Stack' in text
        assert 'top' in text
        assert 'push' in text
        assert 'pop' in text
        assert 'isEmpty' in text
        assert 'new' in text
        assert '50' in text
        assert 'LimitedStack' in text
        assert '12' in text

    def test_code_success_run1(self):
        """Корректный Stack + LimitedStack (ignore) на динамическом массиве."""
        assert self.question1.test(r"""
template<typename T>
class Stack {
    T* data;
    int sz;
public:
    Stack() : data(new T[50]), sz(0) {}
    ~Stack() { delete[] data; }
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz - 1]; }
    bool isEmpty()   { return sz == 0; }
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0;
public:
    void push(T val) {
        if (size_ < 12) { Stack<T>::push(val); size_++; }
    }
};
        """) == Result.Ok()

    def test_code_compile_error1(self):
        """Синтаксическая ошибка в Stack (нет ; после поля), но new есть."""
        with pytest.raises(utility.CompilationError):
            self.question1.test(r"""
template<typename T>
class Stack {
    T* data = new T[50]   // ОШИБКА: нет ;
    int sz;
public:
    Stack() : sz(0) {}
    ~Stack() { delete[] data; }
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz - 1]; }
    bool isEmpty()   { return sz == 0; }
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0;
public:
    void push(T val) {
        if (size_ < 12) { Stack<T>::push(val); size_++; }
    }
};
            """)

    def test_code_compile_error2(self):
        """Синтаксическая ошибка в LimitedStack (нет ; после поля)."""
        with pytest.raises(utility.CompilationError):
            self.question1.test(r"""
template<typename T>
class Stack {
    T* data;
    int sz;
public:
    Stack() : data(new T[50]), sz(0) {}
    ~Stack() { delete[] data; }
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz - 1]; }
    bool isEmpty()   { return sz == 0; }
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0
public:    // ОШИБКА: нет ;
    void push(T val) {
        if (size_ < 12) { Stack<T>::push(val); size_++; }
    }
};
            """)


    def test_code_runtime_error1(self):
        """Stack с буфером 2 — переполняется."""
        assert self.question1.test(r"""
template<typename T>
class Stack {
    T* data;
    int sz;
public:
    Stack() : data(new T[2]), sz(0) {}
    ~Stack() { delete[] data; }
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz - 1]; }
    bool isEmpty()   { return sz == 0; }
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0;
public:
    void push(T val) {
        if (size_ < 12) { Stack<T>::push(val); size_++; }
    }
};
        """) != Result.Ok()

    def test_code_runtime_error2(self):
        """LimitedStack с лимитом 100 вместо 12 — будет пушить больше чем Stack выдержит."""
        assert self.question1.test(r"""
template<typename T>
class Stack {
    T* data;
    int sz;
public:
    Stack() : data(new T[2]), sz(0) {}
    ~Stack() { delete[] data; }
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz - 1]; }
    bool isEmpty()   { return sz == 0; }
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0;
public:
    void push(T val) {
        if (size_ < 100) { Stack<T>::push(val); size_++; }
    }
};
        """) != Result.Ok()

    def test_code_wrong_answer1(self):
        """top() возвращает неверный элемент (off-by-one)."""
        assert self.question1.test(r"""
template<typename T>
class Stack {
    T* data;
    int sz;
public:
    Stack() : data(new T[50]), sz(0) {}
    ~Stack() { delete[] data; }
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz]; }   // ОШИБКА: off-by-one
    bool isEmpty()   { return sz == 0; }
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0;
public:
    void push(T val) {
        if (size_ < 12) { Stack<T>::push(val); size_++; }
    }
};
        """) != Result.Ok()

    def test_code_wrong_answer2(self):
        """isEmpty() инвертирован."""
        assert self.question1.test(r"""
template<typename T>
class Stack {
    T* data;
    int sz;
public:
    Stack() : data(new T[50]), sz(0) {}
    ~Stack() { delete[] data; }
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz - 1]; }
    bool isEmpty()   { return sz != 0; }   // ОШИБКА: инвертировано
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0;
public:
    void push(T val) {
        if (size_ < 12) { Stack<T>::push(val); size_++; }
    }
};
        """) != Result.Ok()

    def test_forbidden_std_stack(self):
        result = self.question1.test(r"""
#include <stack>
template<typename T>
class Stack {
    std::stack<T> s;
public:
    Stack() {} ~Stack() {}
    void push(T val) { s.push(val); }
    void pop()       { s.pop(); }
    T    top()       { return s.top(); }
    bool isEmpty()   { return s.empty(); }
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0;
public:
    void push(T val) {
        if (size_ < 12) { Stack<T>::push(val); size_++; }
    }
};
        """)
        assert result != Result.Ok()

    def test_forbidden_no_new(self):
        result = self.question1.test(r"""
template<typename T>
class Stack {
    T   data[50];
    int sz = 0;
public:
    Stack() {}  ~Stack() {}
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz - 1]; }
    bool isEmpty()   { return sz == 0; }
};

template<typename T>
class LimitedStack : public Stack<T> {
    int size_ = 0;
public:
    void push(T val) {
        if (size_ < 12) { Stack<T>::push(val); size_++; }
    }
};
        """)
        assert result != Result.Ok()


    def test_code_wrong_limit(self):
        """LimitedStack не проверяет лимит — пропускает все push."""
        assert self.question1.test(r"""
template<typename T>
class Stack {
    T* data;
    int sz;
public:
    Stack() : data(new T[50]), sz(0) {}
    ~Stack() { delete[] data; }
    void push(T val) { data[sz++] = val; }
    void pop()       { if (sz > 0) sz--; }
    T    top()       { return data[sz - 1]; }
    bool isEmpty()   { return sz == 0; }
};

template<typename T>
class LimitedStack : public Stack<T> {
public:
    void push(T val) {
        Stack<T>::push(val);   // ОШИБКА: лимит не проверяется
    }
};
        """) != Result.Ok()