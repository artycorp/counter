#ifndef TABLEVIEWCLICKED_H
#define TABLEVIEWCLICKED_H

#include <QTableWidget>

class TableViewClicked : public QTableWidget
{
    Q_OBJECT
public:
    explicit TableViewClicked(QWidget *parent = 0);
    void keyPressEvent (QKeyEvent * e);
    void AddRow();
    void RemoveRow();
signals:

public slots:

};

#endif // TABLEVIEWCLICKED_H
