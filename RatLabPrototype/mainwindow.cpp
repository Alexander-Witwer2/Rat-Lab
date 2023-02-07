#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include <QTableWidget>
#include <QFile>
#include <QTextStream>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    loadTextFile();
}

MainWindow::~MainWindow()
{
    delete ui;
}


void MainWindow::on_pushButton_clicked()
{
    if(ui->table->columnCount() !=1){
        ui->table->insertColumn(0);
        ui->table->setHorizontalHeaderLabels(QString("Name;John").split(";"));
    }
    QString ratName = ui->lineEdit->text();
    ui->table->insertRow(0);
    ui->table->setItem(0,0,new QTableWidgetItem(ratName));
    ui->lineEdit->clear();

    QFile outputFile("C:/Users/zande/OneDrive/Documents/RatLabPrototype/RATNAMES.txt");
    if(outputFile.open(QIODevice::ReadWrite | QIODevice::Append | QIODevice::Text)){
        QTextStream out(&outputFile);
            out << "\n" << ratName;
            outputFile.close();
        qDebug() << "im here!";
    }


    loadTextFile();
}

void MainWindow::loadTextFile(){
    QFile inputFile(":/RATNAMES.txt");
    inputFile.open(QIODevice::ReadOnly | QIODevice::Text);

    QTextStream in(&inputFile);
       QString line = in.readAll();
       inputFile.close();

    ui->textEdit->setPlainText(line);
    QTextCursor cursor = ui->textEdit->textCursor();
    cursor.movePosition(QTextCursor::Start, QTextCursor::MoveAnchor, 1);
}
