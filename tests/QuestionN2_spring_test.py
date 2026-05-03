from prog_questions.spring.QuestionN2 import QuestionN2
from prog_questions import Result, utility
from utility import moodleInit
import pytest


class TestQuestionN2_Basic:
    """Базовые тесты структуры задания и препроцессинга"""
    question = moodleInit(QuestionN2, seed=100, allowed_tasks=[
                          '1'], list_type_override='singly')

    def test_code_preload(self):
        """Препроцессированный код должен компилироваться без ошибок"""
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self):
        """Текст задания должен содержать ключевые фразы"""
        txt = self.question.questionText
        assert 'односвязный' in txt or 'двусвязный' in txt
        assert 'Формат входных данных' in txt
        assert 'Seed' in txt


class TestQuestionN2_Singly:
    """Тесты для односвязных списков (задания 1, 3, 4)"""
    question = moodleInit(QuestionN2, seed=200, allowed_tasks=[
                          '1', '3', '4'], list_type_override='singly')

    def test_swap_nodes_success(self):
        """Задание 1: перестановка двух узлов"""
        self.question.task_id = '1'
        self.question._generate_task_parameters()
        code = r'''
            #include <stdio.h>
            #include <stdlib.h>
            typedef struct Node { int data; struct Node* next; } Node;
            int main() {
                int n, i, j;
                if (scanf("%d", &n) != 1) return 1;
                Node* head = NULL, *tail = NULL;
                for (int k = 0; k < n; k++) {
                    int v; scanf("%d", &v);
                    Node* p = (Node*)malloc(sizeof(Node));
                    p->data = v; p->next = NULL;
                    if (!head) head = tail = p;
                    else { tail->next = p; tail = p; }
                }
                scanf("%d %d", &i, &j);
                Node* pi = head, *pj = head;
                for (int k = 1; k < i; k++) pi = pi->next;
                for (int k = 1; k < j; k++) pj = pj->next;
                if (pi && pj) { int tmp = pi->data; pi->data = pj->data; pj->data = tmp; }
                for (Node* c = head; c; c = c->next) {
                    printf("%d", c->data);
                    if (c->next) printf(" ");
                }
                printf("\n");
                Node* c = head;
                while (c) { Node* nx = c->next; free(c); c = nx; }
                return 0;
            }
        '''
        assert self.question.test(code) == Result.Ok()

    def test_reverse_success(self):
        """Задание 3: разворот списка"""
        self.question.task_id = '3'
        self.question._generate_task_parameters()
        code = r'''
            #include <stdio.h>
            #include <stdlib.h>
            typedef struct Node { int data; struct Node* next; } Node;
            int main() {
                int n;
                if (scanf("%d", &n) != 1) return 1;
                Node* head = NULL;
                for (int k = 0; k < n; k++) {
                    int v; scanf("%d", &v);
                    Node* p = (Node*)malloc(sizeof(Node));
                    p->data = v; p->next = head;
                    head = p;
                }
                for (Node* c = head; c; c = c->next) {
                    printf("%d", c->data);
                    if (c->next) printf(" ");
                }
                printf("\n");
                return 0;
            }
        '''
        assert self.question.test(code) == Result.Ok()

    def test_cyclic_shift_success(self):
        """Задание 4: циклический сдвиг (через односвязный список, без зацикливания)"""
        self.question.task_id = '4'
        self.question._generate_task_parameters()
        code = r'''
            #include <stdio.h>
            #include <stdlib.h>

            typedef struct Node {
                int data;
                struct Node* next;
            } Node;

            int main() {
                int n, k, dir;
                if (scanf("%d", &n) != 1) return 1;
                Node *head = NULL, *tail = NULL;
                for (int i = 0; i < n; i++) {
                    int v; scanf("%d", &v);
                    Node* p = (Node*)malloc(sizeof(Node));
                    p->data = v;
                    p->next = NULL;

                    if (!head) head = tail = p;
                    else {
                        tail->next = p;
                        tail = p;
                    }
                }
                scanf("%d %d", &k, &dir);
                if (n > 1) {
                    k %= n;
                    if (k != 0) {
                        int shift;
                        if (dir == 1) {
                            // сдвиг вправо
                            shift = n - k;
                        } else {
                            // сдвиг влево
                            shift = k;
                        }
                        Node* new_tail = head;
                        for (int i = 1; i < shift; i++) {
                            new_tail = new_tail->next;
                        }
                        Node* new_head = new_tail->next;
                        new_tail->next = NULL;
                        tail->next = head;

                        head = new_head;
                    }
                }
                for (Node* c = head; c; c = c->next) {
                    printf("%d", c->data);
                    if (c->next) printf(" ");
                }
                printf("\n");
                Node* c = head;
                while (c) {
                    Node* nx = c->next;
                    free(c);
                    c = nx;
                }
                return 0;
            }
        '''
        assert self.question.test(code) == Result.Ok()


class TestQuestionLists_Doubly:
    """Тесты для двусвязных списков (задания 5, 6)"""
    question = moodleInit(QuestionN2, seed=300, allowed_tasks=[
                          '5', '6'], list_type_override='doubly')

    def test_insert_sorted_success(self):
        """Задание 5: вставка в отсортированный двусвязный список"""
        self.question.task_id = '5'
        self.question._generate_task_parameters()
        code = r'''
            #include <stdio.h>
            #include <stdlib.h>
            typedef struct Node { int data; struct Node *prev, *next; } Node;
            int main() {
                int n;
                if (scanf("%d", &n) != 1) return 1;
                Node* head = NULL, *tail = NULL;
                for (int i = 0; i < n; i++) {
                    int v; scanf("%d", &v);
                    Node* p = (Node*)malloc(sizeof(Node));
                    p->data = v; p->next = NULL; p->prev = tail;
                    if (!head) head = tail = p;
                    else { tail->next = p; tail = p; }
                }
                int val; scanf("%d", &val);
                Node* new_n = (Node*)malloc(sizeof(Node));
                new_n->data = val; new_n->next = new_n->prev = NULL;
                if (!head) head = tail = new_n;
                else if (val <= head->data) {
                    new_n->next = head; head->prev = new_n; head = new_n;
                } else {
                    Node* c = head;
                    while (c->next && c->next->data < val) c = c->next;
                    new_n->next = c->next; new_n->prev = c;
                    if (c->next) c->next->prev = new_n;
                    else tail = new_n;
                    c->next = new_n;
                }
                for (Node* c = head; c; c = c->next) {
                    printf("%d", c->data);
                    if (c->next) printf(" ");
                }
                printf("\n");
                return 0;
            }
        '''
        assert self.question.test(code) == Result.Ok()

    def test_delete_nodes_success(self):
        """Задание 6: удаление узлов по значению"""
        self.question.task_id = '6'
        self.question._generate_task_parameters()
        code = r'''
            #include <stdio.h>
            #include <stdlib.h>
            typedef struct Node { int data; struct Node *prev, *next; } Node;
            int main() {
                int n;
                if (scanf("%d", &n) != 1) return 1;
                Node* head = NULL, *tail = NULL;
                for (int i = 0; i < n; i++) {
                    int v; scanf("%d", &v);
                    Node* p = (Node*)malloc(sizeof(Node));
                    p->data = v; p->next = NULL; p->prev = tail;
                    if (!head) head = tail = p;
                    else { tail->next = p; tail = p; }
                }
                int target; scanf("%d", &target);
                Node* c = head;
                while (c && c->data == target) {
                    head = c->next;
                    if (head) head->prev = NULL;
                    free(c); c = head;
                }
                c = head;
                while (c && c->next) {
                    if (c->next->data == target) {
                        Node* rem = c->next;
                        c->next = rem->next;
                        if (rem->next) rem->next->prev = c;
                        else tail = c;
                        free(rem);
                    } else c = c->next;
                }
                for (Node* cur = head; cur; cur = cur->next) {
                    printf("%d", cur->data);
                    if (cur->next) printf(" ");
                }
                printf("\n");
                return 0;
            }
        '''
        assert self.question.test(code) == Result.Ok()


class TestQuestionLists_Errors:
    """Тесты на обработку ошибок студентом"""
    question = moodleInit(QuestionN2, seed=400, allowed_tasks=['1'])

    def test_compile_error(self):
        """Должен выбрасываться CompilationError при синтаксической ошибке"""
        self.question.task_id = '1'
        with pytest.raises(utility.CompilationError):
            self.question.test(r'''
                #include <stdio.h>
                int main() {
                    int x = ; // Syntax error
                    return 0;
                }
            ''')

    def test_runtime_error(self):
        """Должен возвращаться Result.Fail при ошибке выполнения (сегфолт)"""
        self.question.task_id = '1'
        assert self.question.test(r'''
            #include <stdio.h>
            int main() {
                int* ptr = NULL;
                *ptr = 5; // Segmentation fault
                return 0;
            }
        ''') != Result.Ok()

    def test_wrong_answer(self):
        """Должен возвращаться Result.Fail при неверном выводе"""
        self.question.task_id = '1'
        # Код просто выводит входной массив без перестановки
        code = r'''
            #include <stdio.h>
            int main() {
                int n;
                scanf("%d", &n);
                for (int i = 0; i < n; i++) {
                    int v; scanf("%d", &v);
                    printf("%d ", v);
                }
                int i, j; scanf("%d %d", &i, &j);
                printf("\n");
                return 0;
            }
        '''
        assert self.question.test(code) != Result.Ok()
