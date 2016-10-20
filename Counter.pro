#-------------------------------------------------
#
# Project created by QtCreator 2016-05-24T21:21:25
#
#-------------------------------------------------


QT       += core gui sql
LIBS    += -lqjson
QMAKE_CXXFLAGS += -std=c++11

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = Counter
TEMPLATE = app


SOURCES += ./src/main.cpp \
        ./src/mainwindow.cpp \
    ./src/tableviewclicked.cpp \
    ./src/logdialog.cpp \
    ./src/logmodel.cpp

HEADERS  += ./h/mainwindow.h \
    ./h/tableviewclicked.h \
    ./h/logdialog.h \
    ./h/logmodel.h

FORMS    += ./ui/mainwindow.ui \
    ./ui/logdialog.ui

RESOURCES += \
    ./img/resources.qrc

