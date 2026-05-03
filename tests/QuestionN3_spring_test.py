from prog_questions.spring import QuestionN3
from prog_questions import Result, utility
from utility import moodleInit
import pytest


class TestQuestionN3:
    question1 = moodleInit(QuestionN3, seed=1)
    question2 = moodleInit(QuestionN3, seed=16)

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

    def test_question_text_2(self):
        text = self.question2.questionText
        assert 'Queue' in text
        assert 'front' in text
        assert 'double' in text
        assert 'односвязного списка' in text
        assert 'LimitedQueue' in text
        assert '8' in text
        assert 'new' in text
        assert '50' in text

    def test_q1_success(self):
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

    def test_q1_compile_error_in_stack(self):
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

    def test_q1_compile_error_in_limited_stack(self):
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

    def test_q1_runtime_error_small_buffer(self):
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

    def test_q1_runtime_error_wrong_limit_too_large(self):
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
        if (size_ < 100) { Stack<T>::push(val); size_++; }  // ОШИБКА: лимит 100 вместо 12
    }
};
        """) != Result.Ok()

    def test_q1_wrong_answer_top_off_by_one(self):
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

    def test_q1_wrong_answer_is_empty_inverted(self):
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

    def test_q1_forbidden_std_stack(self):
        assert self.question1.test(r"""
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
        """) != Result.Ok()

    def test_q1_forbidden_no_new(self):
        assert self.question1.test(r"""
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
        """) != Result.Ok()

    def test_q1_wrong_limit_no_check(self):
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


    def test_q2_success(self):
        """Queue(double, list) + LimitedQueue(evict=8) — проверка FIFO и вытеснения."""

        code = r"""
    class Queue {
        struct Node {
            double val;
            Node* next;
            Node(double v) : val(v), next(nullptr) {}
        };

        Node* head;
        Node* tail;
        int sz;

    public:
        Queue() : head(nullptr), tail(nullptr), sz(0) {}

        ~Queue() {
            while (head) {
                Node* tmp = head;
                head = head->next;
                delete tmp;
            }
        }

        void push(double val) {
            Node* n = new Node(val);
            if (!tail) head = tail = n;
            else { tail->next = n; tail = n; }
            sz++;
        }

        void pop() {
            if (!head) return;
            Node* tmp = head;
            head = head->next;
            delete tmp;
            sz--;
            if (!head) tail = nullptr;
        }

        double front() {
            return head->val;
        }

        bool isEmpty() {
            return sz == 0;
        }

        int size() { return sz; }
    };

    class LimitedQueue : public Queue {
    public:
        void push(double val) {
            if (size() < 8) {
                Queue::push(val);
            } else {
                Queue::pop();
                Queue::push(val);
            }
        }
    };
    """

        result = self.question2.test(code)

        assert result == Result.Ok()

    def test_q2_compile_error_in_queue(self):
        with pytest.raises(utility.CompilationError):
            self.question2.test(r"""
class Queue {
    struct Node {
        double val
        Node* next;              // ОШИБКА: нет ;
        Node(double v) : val(v), next(nullptr) {}
    };
    Node* head;
    Node* tail;
    int sz;
public:
    Queue() : head(nullptr), tail(nullptr), sz(0) {}
    ~Queue() {
        while (head) { Node* tmp = head; head = head->next; delete tmp; }
    }
    void push(double val) {
        Node* n = new Node(val);
        if (!tail) { head = tail = n; }
        else { tail->next = n; tail = n; }
        sz++;
    }
    void pop() {
        if (!head) return;
        Node* tmp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete tmp;
        sz--;
    }
    double front() { return head->val; }
    bool isEmpty() { return sz == 0; }
};

class LimitedQueue : public Queue {
    int size_ = 0;
public:
    void push(double val) {
        if (size_ < 8) { Queue::push(val); size_++; }
        else { Queue::pop(); Queue::push(val); }
    }
};
            """)

    def test_q2_compile_error_in_limited_queue(self):
        with pytest.raises(utility.CompilationError):
            self.question2.test(r"""
class Queue {
    struct Node {
        double val;
        Node* next;
        Node(double v) : val(v), next(nullptr) {}
    };
    Node* head;
    Node* tail;
    int sz;
public:
    Queue() : head(nullptr), tail(nullptr), sz(0) {}
    ~Queue() {
        while (head) { Node* tmp = head; head = head->next; delete tmp; }
    }
    void push(double val) {
        Node* n = new Node(val);
        if (!tail) { head = tail = n; }
        else { tail->next = n; tail = n; }
        sz++;
    }
    void pop() {
        if (!head) return;
        Node* tmp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete tmp;
        sz--;
    }
    double front() { return head->val; }
    bool isEmpty() { return sz == 0; }
};

class LimitedQueue : public Queue {
    int size_ = 0
public:                          // ОШИБКА: нет ;
    void push(double val) {
        if (size_ < 8) { Queue::push(val); size_++; }
        else { Queue::pop(); Queue::push(val); }
    }
};
            """)

    def test_q2_runtime_error_no_tail_update(self):
        assert self.question2.test(r"""
class Queue {
    struct Node {
        double val;
        Node* next;
        Node(double v) : val(v), next(nullptr) {}
    };
    Node* head;
    Node* tail;
    int sz;
public:
    Queue() : head(nullptr), tail(nullptr), sz(0) {}
    ~Queue() {
        while (head) { Node* tmp = head; head = head->next; delete tmp; }
    }
    void push(double val) {
        Node* n = new Node(val);
        if (!tail) { head = tail = n; }
        else { tail->next = n; tail = n; }
        sz++;
    }
    void pop() {
        if (!head) return;
        Node* tmp = head;
        head = head->next;
        // ОШИБКА: tail не обнуляется когда список опустел
        delete tmp;
        sz--;
    }
    double front() { return head->val; }
    bool isEmpty() { return sz == 0; }
};

class LimitedQueue : public Queue {
    int size_ = 0;
public:
    void push(double val) {
        if (size_ < 8) { Queue::push(val); size_++; }
        else { Queue::pop(); Queue::push(val); }
    }
};
        """) != Result.Ok()

    def test_q2_wrong_answer_front_off_by_one(self):
        assert self.question2.test(r"""
class Queue {
    struct Node {
        double val;
        Node* next;
        Node(double v) : val(v), next(nullptr) {}
    };
    Node* head;
    Node* tail;
    int sz;
public:
    Queue() : head(nullptr), tail(nullptr), sz(0) {}
    ~Queue() {
        while (head) { Node* tmp = head; head = head->next; delete tmp; }
    }
    void push(double val) {
        Node* n = new Node(val);
        if (!tail) { head = tail = n; }
        else { tail->next = n; tail = n; }
        sz++;
    }
    void pop() {
        if (!head) return;
        Node* tmp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete tmp;
        sz--;
    }
    double front() { return head->next->val; }  // ОШИБКА: пропускает первый узел
    bool isEmpty() { return sz == 0; }
};

class LimitedQueue : public Queue {
    int size_ = 0;
public:
    void push(double val) {
        if (size_ < 8) { Queue::push(val); size_++; }
        else { Queue::pop(); Queue::push(val); }
    }
};
        """) != Result.Ok()

    def test_q2_wrong_answer_is_empty_inverted(self):
        assert self.question2.test(r"""
class Queue {
    struct Node {
        double val;
        Node* next;
        Node(double v) : val(v), next(nullptr) {}
    };
    Node* head;
    Node* tail;
    int sz;
public:
    Queue() : head(nullptr), tail(nullptr), sz(0) {}
    ~Queue() {
        while (head) { Node* tmp = head; head = head->next; delete tmp; }
    }
    void push(double val) {
        Node* n = new Node(val);
        if (!tail) { head = tail = n; }
        else { tail->next = n; tail = n; }
        sz++;
    }
    void pop() {
        if (!head) return;
        Node* tmp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete tmp;
        sz--;
    }
    double front() { return head->val; }
    bool isEmpty() { return sz != 0; }  // ОШИБКА: инвертировано
};

class LimitedQueue : public Queue {
    int size_ = 0;
public:
    void push(double val) {
        if (size_ < 8) { Queue::push(val); size_++; }
        else { Queue::pop(); Queue::push(val); }
    }
};
        """) != Result.Ok()

    def test_q2_wrong_limit_evict_becomes_ignore(self):
        assert self.question2.test(r"""
class Queue {
    struct Node {
        double val;
        Node* next;
        Node(double v) : val(v), next(nullptr) {}
    };
    Node* head;
    Node* tail;
    int sz;
public:
    Queue() : head(nullptr), tail(nullptr), sz(0) {}
    ~Queue() {
        while (head) { Node* tmp = head; head = head->next; delete tmp; }
    }
    void push(double val) {
        Node* n = new Node(val);
        if (!tail) { head = tail = n; }
        else { tail->next = n; tail = n; }
        sz++;
    }
    void pop() {
        if (!head) return;
        Node* tmp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete tmp;
        sz--;
    }
    double front() { return head->val; }
    bool isEmpty() { return sz == 0; }
};

class LimitedQueue : public Queue {
    int size_ = 0;
public:
    void push(double val) {
        if (size_ < 8) {
            Queue::push(val);
            size_++;
        }
        // ОШИБКА: при переполнении ничего не делаем (ignore вместо evict)
    }
};
        """) != Result.Ok()

    def test_q2_wrong_limit_no_check(self):
        assert self.question2.test(r"""
class Queue {
    struct Node {
        double val;
        Node* next;
        Node(double v) : val(v), next(nullptr) {}
    };
    Node* head;
    Node* tail;
    int sz;
public:
    Queue() : head(nullptr), tail(nullptr), sz(0) {}
    ~Queue() {
        while (head) { Node* tmp = head; head = head->next; delete tmp; }
    }
    void push(double val) {
        Node* n = new Node(val);
        if (!tail) { head = tail = n; }
        else { tail->next = n; tail = n; }
        sz++;
    }
    void pop() {
        if (!head) return;
        Node* tmp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete tmp;
        sz--;
    }
    double front() { return head->val; }
    bool isEmpty() { return sz == 0; }
};

class LimitedQueue : public Queue {
public:
    void push(double val) {
        Queue::push(val);  // ОШИБКА: лимит не проверяется
    }
};
        """) != Result.Ok()

    def test_q2_forbidden_std_queue(self):
        assert self.question2.test(r"""
#include <queue>
class Queue {
    std::queue<double> q;
public:
    Queue() {}  ~Queue() {}
    void push(double val) { q.push(val); }
    void pop()            { q.pop(); }
    double front()        { return q.front(); }
    bool isEmpty()        { return q.empty(); }
};

class LimitedQueue : public Queue {
    int size_ = 0;
public:
    void push(double val) {
        if (size_ < 8) { Queue::push(val); size_++; }
        else { Queue::pop(); Queue::push(val); }
    }
};
        """) != Result.Ok()

    def test_q2_forbidden_no_new(self):
        assert self.question2.test(r"""
class Queue {
    double data[50];
    int head_idx, tail_idx, sz;
public:
    Queue() : head_idx(0), tail_idx(0), sz(0) {}
    ~Queue() {}
    void push(double val) { data[tail_idx++ % 50] = val; sz++; }
    void pop()            { if (sz > 0) { head_idx++; sz--; } }
    double front()        { return data[head_idx % 50]; }
    bool isEmpty()        { return sz == 0; }
};

class LimitedQueue : public Queue {
    int size_ = 0;
public:
    void push(double val) {
        if (size_ < 8) { Queue::push(val); size_++; }
        else { Queue::pop(); Queue::push(val); }
    }
};
        """) != Result.Ok()
