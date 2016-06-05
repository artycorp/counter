#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "logdialog.h"
#include "ui_logdialog.h"
#include <qdebug.h>
#include <qfile.h>
#include <qjson/parser.h>
#include <qjson/serializer.h>
#include <QTableWidget>


MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}
QTableWidgetItem* initValue(QString str)
{
    QTableWidgetItem* item = new QTableWidgetItem(str);
    item->setTextAlignment(Qt::AlignCenter | Qt::AlignVCenter);
    return item;
}

void ReadJson(QTableWidget* table)
{
    //QString val;
    bool ok;
    QFile file;
    file.setFileName("settings.json");
    file.open(QIODevice::ReadOnly | QIODevice::Text);
    QJson::Parser parser;
    QVariantMap res = parser.parse(&file,&ok).toMap();
    //val = file.readAll();
    file.close();
    //qDebug() << res;

    if (ok){
        int i = 0;
        foreach(QVariant search_text, res["search_texts"].toList()){
            int j = 0;
            QVariantMap item = search_text.toMap();
            table->insertRow(i);
            table->setItem(i,  j,initValue(item["text"].toString()));
            QVariantList urls = item["urls"].toList();
            QString str;
            foreach(QVariant url, urls){
                str += url.toString() + ";";
            }
            table->setItem(i,++j,initValue(str));
            table->setItem(i,++j,initValue(item["site_url"].toString()));
            i++;
        }
    }

}

void WriteJson(QTableWidget* table)
{
    QFile file;
    int cntRow = table->rowCount();

    file.setFileName("settings.json");
    file.open(QIODevice::WriteOnly);
    QTextStream out(&file);
    //out.setCodec("UTF-8");
    //out.setGenerateByteOrderMark(true);
    QJson::Serializer serializer;
    QVariantList search_texts;
    for (int i=0;i < cntRow;i++){
        QVariantMap search_text;
        search_text.insert("text", table->item(i,0)->text());
        //search_text.insert("urls", table->item(i,1)->text());
        QVariantList urlsList;
        QString urls = table->item(i,1)->text();
        QStringList list = urls.split(';');
        foreach (QString url, list) {
            urlsList.push_back(url);
        }
        search_text.insert("urls",urlsList);
        search_text.insert("site_url",table->item(i,2)->text());

        search_texts.push_back(search_text);
    }
    bool ok;

    QVariantMap res;
    res.insert("search_texts",search_texts);
    out << serializer.serialize(res,&ok);
    out.flush();
    file.close();
}

void InsertCol(QTableWidget* table, int index, const QString& txt)
{
    QTableWidgetItem* item = new QTableWidgetItem(txt,QTableWidgetItem::Type);
    table->setHorizontalHeaderItem(index, item);
}

void MainWindow::showEvent(QShowEvent *event)
{
    //qDebug() << ui->tableWidget->objectName();
    QTableWidget* table = (ui->tableWidget);

    table->setColumnCount(3);

    InsertCol(table, 0,QString("text"));
    InsertCol(table, 1,QString("urls"));
    InsertCol(table, 2,QString("site_url"));

    /*resize*/
    table->setColumnWidth(0,250);
    table->setColumnWidth(1,250);
    table->setColumnWidth(2,260);

    ReadJson(table);
    QMainWindow::showEvent(event);
}


void MainWindow::on_btInsert_clicked()
{
    ui->tableWidget->AddRow();
}

void MainWindow::on_btRemove_clicked()
{
    ui->tableWidget->RemoveRow();
}

void MainWindow::on_btSave_clicked()
{
    WriteJson(ui->tableWidget);
}

void MainWindow::on_btRun_clicked()
{
    // Save data
    on_btSave_clicked();

    p.kill();
    QStringList params;
    qDebug() << ui->spinCnt->value();
    params << "counter.py" << QString::number(ui->spinCnt->value());
    qDebug() << params;
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
