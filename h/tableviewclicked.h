#ifndef TABLEVIEWCLICKED_H
#define TABLEVIEWCLICKED_H

#include <QTableWidget>
#include <QTableView>

class TableViewClicked : public QTableView
{
    Q_OBJECT
private:
    const bool isEmptyRow(const int);
public:
    explicit TableViewClicked(QWidget *parent = 0);
    void AddRow();
    void RemoveRow();
signals:

public slots:

};

#endif // TABLEVIEWCLICKED_H
