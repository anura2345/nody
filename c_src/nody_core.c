#include "nody_core.h"
#include <stdlib.h>
#include <string.h>
#include <float.h>

CNode* cnode_create(size_t capacity) {
    if (capacity == 0) {
        return NULL;
    }
    CNode* node = (CNode*)malloc(sizeof(CNode));
    if (!node) return NULL;

    node->capacity = capacity;
    node->count = 0;
    node->array = (double*)malloc(capacity * sizeof(double));
    if (!node->array) {
        free(node);
        return NULL;
    }
    node->next = NULL;
    node->prev = NULL;
    return node;
}

void cnode_free(CNode* node) {
    if (node) {
        if (node->array) {
            free(node->array);
            node->array = NULL;
        }
        free(node);
    }
}

int cnode_append(CNode* node, double value) {
    if (!node || node->count >= node->capacity) {
        return 0; /* Failed / Full */
    }
    node->array[node->count++] = value;
    return 1; /* Success */
}

int cnode_insert(CNode* node, size_t index, double value) {
    if (!node || node->count >= node->capacity || index > node->count) {
        return 0;
    }
    if (index < node->count) {
        memmove(&node->array[index + 1], &node->array[index], (node->count - index) * sizeof(double));
    }
    node->array[index] = value;
    node->count++;
    return 1;
}

int cnode_pop(CNode* node, size_t index, double* out_val) {
    if (!node || node->count == 0 || index >= node->count) {
        return 0;
    }
    if (out_val) {
        *out_val = node->array[index];
    }
    if (index + 1 < node->count) {
        memmove(&node->array[index], &node->array[index + 1], (node->count - index - 1) * sizeof(double));
    }
    node->count--;
    return 1;
}

int cnode_get(const CNode* node, size_t index, double* out_val) {
    if (!node || index >= node->count) {
        return 0;
    }
    if (out_val) {
        *out_val = node->array[index];
    }
    return 1;
}

int cnode_set(CNode* node, size_t index, double value) {
    if (!node || index >= node->count) {
        return 0;
    }
    node->array[index] = value;
    return 1;
}

uintptr_t cnode_get_address(const CNode* node) {
    return (uintptr_t)node;
}

uintptr_t cnode_get_next_address(const CNode* node) {
    return node ? (uintptr_t)node->next : 0;
}

uintptr_t cnode_get_prev_address(const CNode* node) {
    return node ? (uintptr_t)node->prev : 0;
}

const double* cnode_get_raw_array(const CNode* node) {
    return node ? node->array : NULL;
}

/* --- Container Operations --- */

CNodyList* cnody_create(size_t node_capacity) {
    if (node_capacity == 0) return NULL;
    CNodyList* list = (CNodyList*)malloc(sizeof(CNodyList));
    if (!list) return NULL;
    list->node_capacity = node_capacity;
    list->total_count = 0;
    list->total_nodes = 0;
    list->head = NULL;
    list->tail = NULL;
    return list;
}

void cnody_free(CNodyList* list) {
    if (!list) return;
    CNode* curr = list->head;
    while (curr) {
        CNode* next = curr->next;
        cnode_free(curr);
        curr = next;
    }
    free(list);
}

void cnody_clear(CNodyList* list) {
    if (!list) return;
    CNode* curr = list->head;
    while (curr) {
        CNode* next = curr->next;
        cnode_free(curr);
        curr = next;
    }
    list->head = NULL;
    list->tail = NULL;
    list->total_count = 0;
    list->total_nodes = 0;
}

int cnody_append(CNodyList* list, double value) {
    if (!list) return 0;

    if (!list->head) {
        CNode* new_node = cnode_create(list->node_capacity);
        if (!new_node) return 0;
        list->head = new_node;
        list->tail = new_node;
        list->total_nodes = 1;
    } else if (list->tail->count >= list->tail->capacity) {
        CNode* new_node = cnode_create(list->node_capacity);
        if (!new_node) return 0;
        list->tail->next = new_node;
        new_node->prev = list->tail;
        list->tail = new_node;
        list->total_nodes++;
    }

    list->tail->array[list->tail->count++] = value;
    list->total_count++;
    return 1;
}

int cnody_prepend(CNodyList* list, double value) {
    if (!list) return 0;

    if (!list->head) {
        CNode* new_node = cnode_create(list->node_capacity);
        if (!new_node) return 0;
        list->head = new_node;
        list->tail = new_node;
        list->total_nodes = 1;
        new_node->array[new_node->count++] = value;
    } else if (list->head->count < list->head->capacity) {
        cnode_insert(list->head, 0, value);
    } else {
        CNode* new_node = cnode_create(list->node_capacity);
        if (!new_node) return 0;
        new_node->next = list->head;
        list->head->prev = new_node;
        list->head = new_node;
        list->total_nodes++;
        new_node->array[new_node->count++] = value;
    }

    list->total_count++;
    return 1;
}

static int cnody_locate(const CNodyList* list, size_t index, CNode** out_node, size_t* out_local_idx) {
    if (!list || index >= list->total_count) return 0;

    if (index < list->total_count / 2) {
        /* Search forward from head */
        CNode* curr = list->head;
        size_t accum = 0;
        while (curr) {
            if (accum + curr->count > index) {
                *out_node = curr;
                *out_local_idx = index - accum;
                return 1;
            }
            accum += curr->count;
            curr = curr->next;
        }
    } else {
        /* Search backward from tail */
        CNode* curr = list->tail;
        size_t accum = list->total_count;
        while (curr) {
            accum -= curr->count;
            if (index >= accum) {
                *out_node = curr;
                *out_local_idx = index - accum;
                return 1;
            }
            curr = curr->prev;
        }
    }
    return 0;
}

int cnody_get(const CNodyList* list, size_t global_index, double* out_val) {
    CNode* node = NULL;
    size_t local_idx = 0;
    if (!cnody_locate(list, global_index, &node, &local_idx)) {
        return 0;
    }
    return cnode_get(node, local_idx, out_val);
}

int cnody_set(CNodyList* list, size_t global_index, double value) {
    CNode* node = NULL;
    size_t local_idx = 0;
    if (!cnody_locate(list, global_index, &node, &local_idx)) {
        return 0;
    }
    return cnode_set(node, local_idx, value);
}

int cnody_insert(CNodyList* list, size_t global_index, double value) {
    if (!list) return 0;
    if (global_index >= list->total_count) {
        return cnody_append(list, value);
    }

    CNode* target = NULL;
    size_t local_idx = 0;
    if (!cnody_locate(list, global_index, &target, &local_idx)) {
        return 0;
    }

    if (target->count < target->capacity) {
        cnode_insert(target, local_idx, value);
    } else {
        /* Split node into two */
        CNode* new_node = cnode_create(list->node_capacity);
        if (!new_node) return 0;

        new_node->next = target->next;
        new_node->prev = target;
        if (target->next) {
            target->next->prev = new_node;
        } else {
            list->tail = new_node;
        }
        target->next = new_node;
        list->total_nodes++;

        /* Move second half to new_node */
        size_t mid = target->count / 2;
        size_t move_count = target->count - mid;
        memcpy(new_node->array, &target->array[mid], move_count * sizeof(double));
        new_node->count = move_count;
        target->count = mid;

        /* Insert into appropriate half */
        if (local_idx <= target->count) {
            cnode_insert(target, local_idx, value);
        } else {
            cnode_insert(new_node, local_idx - target->count, value);
        }
    }

    list->total_count++;
    return 1;
}

int cnody_pop(CNodyList* list, size_t global_index, double* out_val) {
    if (!list || list->total_count == 0 || global_index >= list->total_count) {
        return 0;
    }

    CNode* target = NULL;
    size_t local_idx = 0;
    if (!cnody_locate(list, global_index, &target, &local_idx)) {
        return 0;
    }

    cnode_pop(target, local_idx, out_val);
    list->total_count--;

    /* Unlink if node became empty */
    if (target->count == 0 && list->head != list->tail) {
        if (target->prev) {
            target->prev->next = target->next;
        } else {
            list->head = target->next;
        }
        if (target->next) {
            target->next->prev = target->prev;
        } else {
            list->tail = target->prev;
        }
        cnode_free(target);
        list->total_nodes--;
    }

    return 1;
}

size_t cnody_len(const CNodyList* list) {
    return list ? list->total_count : 0;
}

size_t cnody_node_count(const CNodyList* list) {
    return list ? list->total_nodes : 0;
}

/* --- High Speed Batch & Math Operations (Zero-overhead C) --- */

void cnody_append_batch(CNodyList* list, const double* src, size_t count) {
    if (!list || !src || count == 0) return;

    size_t offset = 0;
    while (offset < count) {
        if (!list->head || list->tail->count >= list->tail->capacity) {
            CNode* new_node = cnode_create(list->node_capacity);
            if (!new_node) return;
            if (!list->head) {
                list->head = list->tail = new_node;
            } else {
                list->tail->next = new_node;
                new_node->prev = list->tail;
                list->tail = new_node;
            }
            list->total_nodes++;
        }

        size_t available = list->tail->capacity - list->tail->count;
        size_t to_copy = (count - offset < available) ? (count - offset) : available;

        memcpy(&list->tail->array[list->tail->count], &src[offset], to_copy * sizeof(double));
        list->tail->count += to_copy;
        list->total_count += to_copy;
        offset += to_copy;
    }
}

size_t cnody_to_buffer(const CNodyList* list, double* dst, size_t max_count) {
    if (!list || !dst || max_count == 0) return 0;

    size_t copied = 0;
    CNode* curr = list->head;
    while (curr && copied < max_count) {
        size_t to_copy = curr->count;
        if (copied + to_copy > max_count) {
            to_copy = max_count - copied;
        }
        memcpy(&dst[copied], curr->array, to_copy * sizeof(double));
        copied += to_copy;
        curr = curr->next;
    }
    return copied;
}

double cnody_sum(const CNodyList* list) {
    if (!list) return 0.0;
    double sum = 0.0;
    CNode* curr = list->head;
    while (curr) {
        const double* arr = curr->array;
        size_t n = curr->count;
        for (size_t i = 0; i < n; ++i) {
            sum += arr[i];
        }
        curr = curr->next;
    }
    return sum;
}

double cnody_min(const CNodyList* list) {
    if (!list || list->total_count == 0) return 0.0;
    double min_val = DBL_MAX;
    CNode* curr = list->head;
    while (curr) {
        const double* arr = curr->array;
        size_t n = curr->count;
        for (size_t i = 0; i < n; ++i) {
            if (arr[i] < min_val) min_val = arr[i];
        }
        curr = curr->next;
    }
    return min_val;
}

double cnody_max(const CNodyList* list) {
    if (!list || list->total_count == 0) return 0.0;
    double max_val = -DBL_MAX;
    CNode* curr = list->head;
    while (curr) {
        const double* arr = curr->array;
        size_t n = curr->count;
        for (size_t i = 0; i < n; ++i) {
            if (arr[i] > max_val) max_val = arr[i];
        }
        curr = curr->next;
    }
    return max_val;
}

void cnody_scale(CNodyList* list, double factor) {
    if (!list) return;
    CNode* curr = list->head;
    while (curr) {
        double* arr = curr->array;
        size_t n = curr->count;
        for (size_t i = 0; i < n; ++i) {
            arr[i] *= factor;
        }
        curr = curr->next;
    }
}
