#include "h/mainwindow.h"
#include "ui_mainwindow.h"
#include "h/logdialog.h"
#include "ui_logdialog.h"
#include <qdebug.h>
#include <qfile.h>
#include <qjson/parser.h>
#include <qjson/serializer.h>
#include<QMessageBox>
#include <QSqlTableModel>


MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow),
    db(QSqlDatabase::addDatabase("QMYSQL"))
{
    db.setHostName("localhost");
    db.setDatabaseName("counter");
    db.setUserName("counter");
    db.setPassword("counter");

    ui->setupUi(this);
    setupModel(ui->tableWidget);
}

MainWindow::~MainWindow()
{
    delete ui;
    db.close();
}

void MainWindow::showEvent(QShowEvent *event)
{

    qDebug() << "Show event";
    QTableView* table = (ui->tableWidget);

    /*resize*/
    table->setColumnWidth(1,250);
    table->setColumnWidth(2,250);
    table->setColumnWidth(3,260);

    //ReadJson(table);
    QMainWindow::showEvent(event);
}


void MainWindow::on_btInsert_clicked()
{
    ui->tableWidget->AddRow();
}

void MainWindow::setupModel(QTableView* table)
{

    if (!db.open()) {
        qDebug() << db.lastError().text();
        QMessageBox::critical(0, tr("Cannot open database"),
            tr("Unable to establish a database connection.\n"
               "This example needs MySQL support. Please read "
               "the Qt SQL driver documentation for information how "
               "to build it."), QMessageBox::Cancel);
        return;
    }

    QSqlTableModel* model = new QSqlTableModel();
    model->setTable("settings");
    model->select();
    model->setEditStrategy(QSqlTableModel::OnManualSubmit);
    //model->setQuery("SELECT `text`,`url`,`site` FROM `counter`.`settings`;",db);
    table->setModel(model);
    table->hideColumn(0);
}


void MainWindow::on_btRemove_clicked()
{
     ui->tableWidget->RemoveRow();
}

void MainWindow::on_btSave_clicked()
{
    QMessageBox msgBox;
    msgBox.setIcon(QMessageBox::Information);
    QSqlTableModel* model = static_cast<QSqlTableModel*>(this->ui->tableWidget->model());
    if (!model->submitAll())
        msgBox.setText(model->lastError().text());
    else
        msgBox.setText("Success save");
    msgBox.exec();
}

void MainWindow::on_btRun_clicked()
{
    // Save data
    on_btSave_clicked();

    p.kill();
    QStringList params;
    qDebug() << ui->spinCnt->value();
    QProcessEnvironment env = QProcessEnvironment::systemEnvironment();
    env.insert("COUNTER_SETTINGS_PATH", "./python/");
    params << "./python/counter.py" << QString::number(ui->spinCnt->value()) << QString::number(ui->spinDepth->value());
    qDebug() << params;
    p.setProcessEnvironment(env);
    p.start("python",params);
    //p.waitForFinished(-1);
    QString p_stdout = p.readAll();
    qDebug() << p_stdout;

}

void MainWindow::on_btStop_clicked()
{
    p.kill();
}

void MainWindow::on_toolButton_clicked()
{
    LogDialog* dlg = new LogDialog(this);
    dlg->show();
}
