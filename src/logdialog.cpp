#include "h/logdialog.h"
#include "ui_logdialog.h"

LogDialog::LogDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::LogDialog)
{
    model = new LogModel(this);
    ui->setupUi(this);    
    ui->tableView->setModel(model);
}

LogDialog::~LogDialog()
{
    delete ui;
}
