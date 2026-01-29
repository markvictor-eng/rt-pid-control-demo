cmake_minimum_required(VERSION 3.10)
project(rt_pid_demo)

set(CMAKE_CXX_STANDARD 17)

add_executable(rt_loop
    main.cpp
    pid.cpp
    plant.cpp
    timing.cpp
    ipc.cpp
)
