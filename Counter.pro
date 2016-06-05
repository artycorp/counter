#-------------------------------------------------
#
# Project created by QtCreator 2016-05-24T21:21:25
#
#-------------------------------------------------


CONFIG   += c++11
QT       += core gui
LIBS    += -lqjson

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = Counter
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp \
    tableviewclicked.cpp \
    logdialog.cpp \
    logmodel.cpp

HEADERS  += mainwindow.h \
    tableviewclicked.h \
    logdialog.h \
    logmodel.h

FORMS    += mainwindow.ui \
    logdialog.ui

RESOURCES += \
    resources.qrc

