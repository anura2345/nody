#ifndef NODY_CORE_H
#define NODY_CORE_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef _WIN32
  #define NODY_API __declspec(dllexport)
#else
  #define NODY_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* A single node in the C Unrolled Linked List */
typedef struct CNode {
    size_t capacity;          /* Fixed size of the internal contiguous C array */
    size_t count;             /* Number of active elements currently in array */
    double* array;            /* Contiguous C array allocated on the heap */
    struct CNode* next;       /* 32/64-bit native pointer to next node */
    struct CNode* prev;       /* 32/64-bit native pointer to previous node */
} CNode;

/* The container list managing the chain of node arrays */
typedef struct CNodyList {
    size_t node_capacity;     /* Fixed array capacity for every node */
    size_t total_count;       /* Total number of elements across all nodes */
    size_t total_nodes;       /* Total number of node blocks currently allocated */
    CNode* head;              /* Pointer to the first node */
    CNode* tail;              /* Pointer to the last node */
} CNodyList;

/* Node-level API */
NODY_API CNode* cnode_create(size_t capacity);
NODY_API void cnode_free(CNode* node);
NODY_API int cnode_append(CNode* node, double value);
NODY_API int cnode_insert(CNode* node, size_t index, double value);
NODY_API int cnode_pop(CNode* node, size_t index, double* out_val);
NODY_API int cnode_get(const CNode* node, size_t index, double* out_val);
NODY_API int cnode_set(CNode* node, size_t index, double value);
NODY_API uintptr_t cnode_get_address(const CNode* node);
NODY_API uintptr_t cnode_get_next_address(const CNode* node);
NODY_API uintptr_t cnode_get_prev_address(const CNode* node);
NODY_API const double* cnode_get_raw_array(const CNode* node);

/* List-level API */
NODY_API CNodyList* cnody_create(size_t node_capacity);
NODY_API void cnody_free(CNodyList* list);
NODY_API int cnody_append(CNodyList* list, double value);
NODY_API int cnody_prepend(CNodyList* list, double value);
NODY_API int cnody_insert(CNodyList* list, size_t global_index, double value);
NODY_API int cnody_pop(CNodyList* list, size_t global_index, double* out_val);
NODY_API int cnody_get(const CNodyList* list, size_t global_index, double* out_val);
NODY_API int cnody_set(CNodyList* list, size_t global_index, double value);
NODY_API size_t cnody_len(const CNodyList* list);
NODY_API size_t cnody_node_count(const CNodyList* list);
NODY_API void cnody_clear(CNodyList* list);

/* High-speed bulk and numerical operations executed in native C */
NODY_API void cnody_append_batch(CNodyList* list, const double* src, size_t count);
NODY_API size_t cnody_to_buffer(const CNodyList* list, double* dst, size_t max_count);
NODY_API double cnody_sum(const CNodyList* list);
NODY_API double cnody_min(const CNodyList* list);
NODY_API double cnody_max(const CNodyList* list);
NODY_API void cnody_scale(CNodyList* list, double factor);

#ifdef __cplusplus
}
#endif

#endif /* NODY_CORE_H */
