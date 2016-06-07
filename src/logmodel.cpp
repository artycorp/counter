#include "h/logmodel.h"
#include <QFile>
#include <QTextStream>
#include <QVector>
#include <QStringList>

LogVector* readFile(){
    QFile f("./python/ui.log");
    LogVector* v = new LogVector();

    f.open(QIODevice::ReadOnly);
    QTextStream in(&f);

    while (!in.atEnd()){
        QString row = in.readLine();
        QStringList list = row.split("|");
        v->push_back(list);
    }

    f.close();
    return v;
}


LogModel::LogModel(QObject *parent) :
    QAbstractTableModel(parent)
{
    v = readFile();
}

int LogModel::rowCount(const QModelIndex &parent) const
{
    return v->count();
}

int LogModel::columnCount(const QModelIndex &parent) const
{
    return 6;
}


QVariant LogModel::data(const QModelIndex &index, int role) const
{

    if (role == Qt::DisplayRole)
    {

        int row = index.row();
        QStringList list = v->at(row);
        int column = index.column();
        return list.at(column);

    }
    return QVariant();
}

QVariant LogModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    if (role != Qt::DisplayRole)
            return QVariant();
    if (orientation == Qt::Horizontal){
        switch (section) {
            case 0:
                return QString::fromUtf8("время");
                break;
            case 1:
                 return QString::fromUtf8("поисковик");
                break;
            case 2:
                return QString::fromUtf8("запрос");
                break;
            case 3:
                return QString::fromUtf8("позиция на странице");
                break;
            case 4:
                return QString::fromUtf8("общая позиция");
                break;
            case 5:
                return QString::fromUtf8("ссылка");
                break;
            default:
                break;
        }
    }
    else
        return section;
    return QVariant();
}
