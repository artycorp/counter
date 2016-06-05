#ifndef LOGMODEL_H
#define LOGMODEL_H

#include <QAbstractTableModel>

typedef QVector<QStringList> LogVector;

class LogModel : public QAbstractTableModel
{
    Q_OBJECT
public:

    explicit LogModel(QObject *parent = 0);
    int rowCount(const QModelIndex &parent = QModelIndex()) const ;
    int columnCount(const QModelIndex &parent = QModelIndex()) const;
    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const;
    QVariant headerData(int section, Qt::Orientation orientation,int role) const;
signals:

public slots:

private:
    LogVector* v;
};

#endif // LOGMODEL_H
