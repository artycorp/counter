#ifndef LOGDIALOG_H
#define LOGDIALOG_H

#include <QDialog>
#include <h/logmodel.h>

namespace Ui {
class LogDialog;
}

class LogDialog : public QDialog
{
    Q_OBJECT

public:
    explicit LogDialog(QWidget *parent = 0);
    ~LogDialog();

private:
    Ui::LogDialog *ui;
    LogModel* model;
};

#endif // LOGDIALOG_H
