if(NOT TARGET hermes-engine::hermesvm)
add_library(hermes-engine::hermesvm SHARED IMPORTED)
set_target_properties(hermes-engine::hermesvm PROPERTIES
    IMPORTED_LOCATION "C:/Users/krist/.gradle/caches/9.0.0/transforms/c1a26c6b9545f2461cca9cf8ec3a5162/transformed/hermes-android-0.82.1-debug/prefab/modules/hermesvm/libs/android.arm64-v8a/libhermesvm.so"
    INTERFACE_INCLUDE_DIRECTORIES "C:/Users/krist/.gradle/caches/9.0.0/transforms/c1a26c6b9545f2461cca9cf8ec3a5162/transformed/hermes-android-0.82.1-debug/prefab/modules/hermesvm/include"
    INTERFACE_LINK_LIBRARIES ""
)
endif()

