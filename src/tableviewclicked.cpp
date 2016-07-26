#include "h/tableviewclicked.h"
#include <QKeyEvent>
#include <QDebug>
#include <QMessageBox>

TableViewClicked::TableViewClicked(QWidget *parent) :
    QTableWidget(parent)
{
}

void TableViewClicked::keyPressEvent(QKeyEvent *e)
{


    switch(e->key())
    {
        case Qt::Key_Insert:
            AddRow();
            break;
            case Qt::Key_Delete:
                RemoveRow();
            break;
    }
    QTableWidget::keyPressEvent(e);
}

//TODO fix! copy/past
QTableWidgetItem* initValue()
{
    QTableWidgetItem* item = new QTableWidgetItem();
    item->setTextAlignment(Qt::AlignCenter | Qt::AlignVCenter);
    return item;
}

void TableViewClicked::AddRow()
{
    int cntRow = this->rowCount();
    this->insertRow(cntRow);

    for (int i=0;i<colorCount();i++){
        setItem(cntRow,i,initValue());
    }
}

const bool TableViewClicked::isEmptyRow(const int rowNum){
    int cntCol = this->columnCount();
    bool bIsNotEmpty = false;
    for (int i=0;i<cntCol;i++){
        QTableWidgetItem* ptr = this->item(rowNum,i);
        if (ptr)
        {
            QString txt = ptr->text();
            if (! txt.isEmpty()){
                bIsNotEmpty = true;
                break;
            }
        }
    }
    return !bIsNotEmpty;
}

void TableViewClicked::RemoveRow()
{
    QModelIndexList selection = this->selectionModel()->selectedRows();
    int rowNum = -1;
    qDebug() << selection.count();

    for(int i=selection.count(); i > 0 ; i--)
    {
        QModelIndex index = selection.at(i-1);

        rowNum = index.row();
        if (!isEmptyRow(rowNum)){
            QMessageBox::StandardButton reply;
            reply = QMessageBox::question(this,  QString::fromUtf8("Удаление строки"), QString::fromUtf8("Удалить не пустую строку?"),QMessageBox::Yes | QMessageBox::No);

            if (reply == QMessageBox::Yes){

                this->removeRow(rowNum);
            }
        }
    }


    /*
    else{
        this->setRowCount(cntRow >0 ? cntRow -1 : 0);
    }
    */
}

