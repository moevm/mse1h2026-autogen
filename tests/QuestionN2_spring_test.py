from prog_questions.spring.QuestionN2 import QuestionN2
from prog_questions import Result, utility
from utility import moodleInit
import pytest


class TestQuestionN2_Basic:
    """Базовые тесты структуры задания и препроцессинга"""
    # allowed_tasks теперь принимает названия операций, а не цифры
    question = moodleInit(QuestionN2, seed=100, allowed_tasks=[
                          'swap'], list_type_override='singly')

    def test_code_preload(self):
        """Препроцессированный код должен компилироваться без ошибок"""
        utility.CProgramRunner(self.question.preloadedCode)

    def test_question_text(self):
        """Текст задания должен содержать ключевые фразы"""
        txt = self.question.questionText
        assert 'односвязный' in txt or 'двусвязный' in txt
        assert 'Формат входных данных' in txt


class TestQuestionN2_Singly:
    """Тесты для односвязных списков (операции: swap, reverse, shift)"""
    question = moodleInit(QuestionN2, seed=200, allowed_tasks=[
                          'swap', 'reverse', 'shift'], list_type_override='singly')

    def _force_config(self, operation: str, num_lists: int = 1):
        """Вспомогательный метод для фиксации конфигурации перед тестом"""
        self.question.config.operation = operation
        self.question.config.num_lists = num_lists
        self.question.config.list_type = 'singly'
        # Обновляем task_id для совместимости, если он где-то используется
        self.question.task_id = self.question.config.task_id
        # Перегенерируем значения списков под новую конфигурацию
        self.question._generate_list_values()

    def test_swap_nodes_success(self):
        """Операция swap: перестановка двух элементов в одном списке"""
        self._force_config('swap', num_lists=1)

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
        """Операция reverse: разворот списка"""
        self._force_config('reverse', num_lists=1)

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
        """Операция shift: циклический сдвиг"""
        self._force_config('shift', num_lists=1)

        code = r'''
            #include <stdio.h>
            #include <stdlib.h>
            typedef struct Node { int data; struct Node* next; } Node;
            int main() {
                int n, k, dir;
                if (scanf("%d", &n) != 1) return 1;
                Node *head = NULL, *tail = NULL;
                for (int i = 0; i < n; i++) {
                    int v; scanf("%d", &v);
                    Node* p = (Node*)malloc(sizeof(Node));
                    p->data = v; p->next = NULL;
                    if (!head) head = tail = p;
                    else { tail->next = p; tail = p; }
                }
                scanf("%d %d", &k, &dir);
                if (n > 1) {
                    k %= n;
                    if (k != 0) {
                        int shift = (dir == 1) ? (n - k) : k;
                        Node* new_tail = head;
                        for (int i = 1; i < shift; i++) new_tail = new_tail->next;
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
                while (c) { Node* nx = c->next; free(c); c = nx; }
                return 0;
            }
        '''
        assert self.question.test(code) == Result.Ok()

    def test_swap_two_lists_success(self):
        """Операция swap: обмен элементами между двумя списками"""
        self._force_config('swap', num_lists=2)

        code = r'''
            #include <stdio.h>
            #include <stdlib.h>
            typedef struct Node { int data; struct Node* next; } Node;
            
            Node* build_list(int n) {
                Node* head = NULL, *tail = NULL;
                for (int k = 0; k < n; k++) {
                    int v; scanf("%d", &v);
                    Node* p = (Node*)malloc(sizeof(Node));
                    p->data = v; p->next = NULL;
                    if (!head) head = tail = p;
                    else { tail->next = p; tail = p; }
                }
                return head;
            }
            
            void print_list(Node* head) {
                for (Node* c = head; c; c = c->next) {
                    printf("%d", c->data);
                    if (c->next) printf(" ");
                }
                printf("\n");
            }
            
            void free_list(Node* head) {
                while (head) { Node* nx = head->next; free(head); head = nx; }
            }
            
            int main() {
                int n, m, pos1, pos2;
                if (scanf("%d", &n) != 1) return 1;
                Node* h1 = build_list(n);
                if (scanf("%d", &m) != 1) return 1;
                Node* h2 = build_list(m);
                scanf("%d %d", &pos1, &pos2);
                
                // Поиск узлов для обмена
                Node* p1 = h1, *p2 = h2;
                for (int k = 1; k < pos1 && p1; k++) p1 = p1->next;
                for (int k = 1; k < pos2 && p2; k++) p2 = p2->next;
                
                if (p1 && p2) {
                    int tmp = p1->data;
                    p1->data = p2->data;
                    p2->data = tmp;
                }
                
                print_list(h1);
                print_list(h2);
                free_list(h1);
                free_list(h2);
                return 0;
            }
        '''
        assert self.question.test(code) == Result.Ok()


class TestQuestionLists_Doubly:
    """Тесты для двусвязных списков (операции: insert, delete)"""
    question = moodleInit(QuestionN2, seed=300, allowed_tasks=[
                          'insert', 'delete'], list_type_override='doubly')

    def _force_config(self, operation: str):
        """Вспомогательный метод для фиксации конфигурации перед тестом"""
        self.question.config.operation = operation
        self.question.config.num_lists = 1
        self.question.config.list_type = 'doubly'
        if operation == 'insert':
            self.question.config.is_sorted = True
        self.question.task_id = self.question.config.task_id
        self.question._generate_list_values()

    def test_insert_sorted_success(self):
        """Операция insert: вставка в отсортированный двусвязный список"""
        self._force_config('insert')

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
        """Операция delete: удаление элементов по значению"""
        self._force_config('delete')

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
    question = moodleInit(QuestionN2, seed=400, allowed_tasks=['swap'])

    def _force_swap_config(self):
        self.question.config.operation = 'swap'
        self.question.config.num_lists = 1
        self.question.task_id = self.question.config.task_id
        self.question._generate_list_values()

    def test_compile_error(self):
        """Должен выбрасываться CompilationError при синтаксической ошибке"""
        self._force_swap_config()
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
        self._force_swap_config()
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
        self._force_swap_config()
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
