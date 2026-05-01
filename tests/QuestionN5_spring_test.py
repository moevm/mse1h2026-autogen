from prog_questions.spring import QuestionN5, Result, utility
from utility import moodleInit
import pytest


def make_question(task_type):
    return moodleInit(QuestionN5, seed=42, taskType=task_type)


class TestQuestionN5_Basic:
    def test_preloaded_code_compiles(self):
        q = make_question('delete_rename')
        utility.CProgramRunner(q.preloadedCode)

    def test_question_text_not_empty(self):
        for task_type in QuestionN5.TASK_TYPES:
            q = make_question(task_type)
            assert len(q.questionText) > 100

    def test_random_task_type_selected_when_empty(self):
        q = moodleInit(QuestionN5, seed=42, taskType='')
        assert q.taskType in QuestionN5.TASK_TYPES


class TestQuestionN5_DeleteRename:
    question = make_question('delete_rename')

    def test_correct(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <stdlib.h>
            #include <string.h>

            int main() {
                char to_delete[256], old_name[256], new_name[256];
                fgets(to_delete, sizeof(to_delete), stdin); to_delete[strcspn(to_delete, "\n")] = '\0';
                fgets(old_name, sizeof(old_name), stdin); old_name[strcspn(old_name, "\n")] = '\0';
                fgets(new_name, sizeof(new_name), stdin); new_name[strcspn(new_name, "\n")] = '\0';
                printf("%s\n", remove(to_delete) == 0 ? "ok" : "error");
                printf("%s\n", rename(old_name, new_name) == 0 ? "ok" : "error");
                return 0;
            }
        ''') == Result.Ok()

    def test_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>
            int main() { printf("error\nerror\n"); return 0; }
        ''') != Result.Ok()

    def test_compile_error(self):
        with pytest.raises(utility.CompilationError):
            self.question.test('int main( { return 0; }')


class TestQuestionN5_ReadHex:
    question = make_question('read_hex')

    def test_correct(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>

            int main() {
                char filename[256];
                long offset;
                int n, group_size;
                fgets(filename, sizeof(filename), stdin); filename[strcspn(filename, "\n")] = '\0';
                scanf("%ld %d %d", &offset, &n, &group_size);
                FILE *f = fopen(filename, "rb");
                if (!f) { fprintf(stderr, "open error\n"); return 1; }
                fseek(f, offset, SEEK_SET);
                int first = 1;
                int remaining = n;
                while (remaining > 0) {
                    if (!first) printf(" ");
                    first = 0;
                    if (group_size == 1) {
                        uint8_t v; fread(&v, 1, 1, f);
                        printf("%02x", v);
                    } else if (group_size == 2) {
                        uint16_t v; fread(&v, 2, 1, f);
                        printf("%04x", v);
                    } else if (group_size == 4) {
                        uint32_t v; fread(&v, 4, 1, f);
                        printf("%08x", v);
                    } else {
                        uint64_t v; fread(&v, 8, 1, f);
                        printf("%016lx", v);
                    }
                    remaining -= group_size;
                }
                printf("\n");
                fclose(f);
                return 0;
            }
        ''') == Result.Ok()

    def test_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>
            int main() { printf("00\n"); return 0; }
        ''') != Result.Ok()


class TestQuestionN5_OverwriteBytes:
    question = make_question('overwrite_bytes')

    def test_correct(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char filename[256];
                long offset;
                char data[256];
                fgets(filename, sizeof(filename), stdin); filename[strcspn(filename, "\n")] = '\0';
                scanf("%ld", &offset); getchar();
                fgets(data, sizeof(data), stdin); data[strcspn(data, "\n")] = '\0';
                FILE *f = fopen(filename, "r+b");
                if (!f) return 1;
                fseek(f, offset, SEEK_SET);
                fwrite(data, 1, strlen(data), f);
                fclose(f);
                return 0;
            }
        ''') == Result.Ok()

    def test_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>
            int main() { return 0; }
        ''') != Result.Ok()


class TestQuestionN5_FileStats:
    question = make_question('file_stats')

    def test_correct(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <string.h>

            int main() {
                char filename[256];
                fgets(filename, sizeof(filename), stdin); filename[strcspn(filename, "\n")] = '\0';

                FILE *f = fopen(filename, "r");
                if (!f) return 1;

                fseek(f, 0, SEEK_END);
                long file_size = ftell(f);
                rewind(f);

                int line_count = 0;
                int longest = 0;
                int current = 0;
                int c;
                while ((c = fgetc(f)) != EOF) {
                    if (c == '\n') {
                        if (current > longest) longest = current;
                        current = 0;
                        line_count++;
                    } else {
                        current++;
                    }
                }

                printf("%ld\n%d\n%d\n", file_size, line_count, longest);
                fclose(f);
                return 0;
            }
        ''') == Result.Ok()

    def test_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>
            int main() { printf("0\n0\n0\n"); return 0; }
        ''') != Result.Ok()


class TestQuestionN5_MergeFiles:
    question = make_question('merge_files')

    def test_correct(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <stdlib.h>
            #include <string.h>

            int main() {
                char src[256], dst[256];
                fgets(src, sizeof(src), stdin); src[strcspn(src, "\n")] = '\0';
                fgets(dst, sizeof(dst), stdin); dst[strcspn(dst, "\n")] = '\0';

                FILE *fsrc = fopen(src, "rb");
                FILE *fdst = fopen(dst, "ab");
                if (!fsrc || !fdst) return 1;

                char buf[4096];
                size_t n;
                while ((n = fread(buf, 1, sizeof(buf), fsrc)) > 0)
                    fwrite(buf, 1, n, fdst);

                fclose(fsrc);
                fclose(fdst);

                FILE *f = fopen(dst, "rb");
                fseek(f, 0, SEEK_END);
                long sz = ftell(f);
                fclose(f);

                printf("%ld\n", sz);
                return 0;
            }
        ''') == Result.Ok()

    def test_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>
            int main() { printf("0\n"); return 0; }
        ''') != Result.Ok()


class TestQuestionN5_ListDirectory:
    question = make_question('list_directory')

    def test_correct(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <stdlib.h>
            #include <string.h>
            #include <dirent.h>
            #include <sys/stat.h>

            int cmp(const void *a, const void *b) {
                return strcmp(*(const char **)a, *(const char **)b);
            }

            int main() {
                char dirpath[256];
                fgets(dirpath, sizeof(dirpath), stdin); dirpath[strcspn(dirpath, "\n")] = '\0';

                DIR *d = opendir(dirpath);
                if (!d) return 1;

                char *names[1024];
                int count = 0;
                struct dirent *entry;
                while ((entry = readdir(d)) != NULL) {
                    if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
                        continue;
                    names[count++] = strdup(entry->d_name);
                }
                closedir(d);

                qsort(names, count, sizeof(char *), cmp);

                for (int i = 0; i < count; i++) {
                    char fullpath[512];
                    snprintf(fullpath, sizeof(fullpath), "%s/%s", dirpath, names[i]);
                    struct stat st;
                    stat(fullpath, &st);
                    const char *type;
                    if (S_ISREG(st.st_mode))       type = "file";
                    else if (S_ISDIR(st.st_mode))  type = "dir";
                    else                            type = "link";
                    printf("%s [%s]\n", names[i], type);
                    free(names[i]);
                }
                return 0;
            }
        ''') == Result.Ok()

    def test_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>
            int main() { return 0; }
        ''') != Result.Ok()


class TestQuestionN5_CountLinesInDir:
    question = make_question('count_lines_in_dir')

    def test_correct(self):
        assert self.question.test(r'''
            #include <stdio.h>
            #include <stdlib.h>
            #include <string.h>
            #include <dirent.h>
            #include <sys/stat.h>

            int cmp(const void *a, const void *b) {
                return strcmp(*(const char **)a, *(const char **)b);
            }

            int count_newlines(const char *path) {
                FILE *f = fopen(path, "r");
                if (!f) return 0;
                int count = 0, c;
                while ((c = fgetc(f)) != EOF)
                    if (c == '\n') count++;
                fclose(f);
                return count;
            }

            int main() {
                char dirpath[256];
                fgets(dirpath, sizeof(dirpath), stdin); dirpath[strcspn(dirpath, "\n")] = '\0';

                DIR *d = opendir(dirpath);
                if (!d) return 1;

                char *names[1024];
                int count = 0;
                struct dirent *entry;
                while ((entry = readdir(d)) != NULL) {
                    if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
                        continue;
                    char fullpath[512];
                    snprintf(fullpath, sizeof(fullpath), "%s/%s", dirpath, entry->d_name);
                    struct stat st;
                    if (stat(fullpath, &st) == 0 && S_ISREG(st.st_mode))
                        names[count++] = strdup(entry->d_name);
                }
                closedir(d);
                qsort(names, count, sizeof(char *), cmp);

                for (int i = 0; i < count; i++) {
                    char fullpath[512];
                    snprintf(fullpath, sizeof(fullpath), "%s/%s", dirpath, names[i]);
                    printf("%s: %d\n", names[i], count_newlines(fullpath));
                    free(names[i]);
                }
                return 0;
            }
        ''') == Result.Ok()

    def test_wrong_answer(self):
        assert self.question.test(r'''
            #include <stdio.h>
            int main() { return 0; }
        ''') != Result.Ok()
