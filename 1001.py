import sys
import csv
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QGroupBox, QGridLayout, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class ScoreTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tracker Punteggio Gioco")
        self.setGeometry(100, 100, 900, 700)
        
        self.player1 = ""
        self.player2 = ""
        self.scores = []
        self.total_player1 = 0
        self.total_player2 = 0
        self.card_dealer_turn = 1  # 1 per player1, 2 per player2
        self.game_active = False
        
        # Variabili per gli accusi
        self.accuse_briscola_used = False
        self.accuse_count = 0
        self.accuse_player1 = 0
        self.accuse_player2 = 0
        
        # Cartella partite
        self.games_folder = "partite"
        if not os.path.exists(self.games_folder):
            os.makedirs(self.games_folder)
        
        self.initUI()
        
    def initUI(self):
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # SEZIONE INPUT GIOCATORI (solo visibile all'inizio)
        self.player_input_widget = QWidget()
        player_input_layout = QVBoxLayout()
        player_input_layout.setSpacing(20)
        
        # Aggiungi l'immagine copertina.png ridimensionata a 3/4
        try:
            cover_label = QLabel()
            pixmap = QPixmap("copertina.png")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    int(pixmap.width() * 0.75), 
                    int(pixmap.height() * 0.75), 
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                cover_label.setPixmap(scaled_pixmap)
                cover_label.setAlignment(Qt.AlignCenter)
                player_input_layout.addWidget(cover_label)
        except:
            pass  # Se l'immagine non viene trovata, continua senza
        
        # Titolo sezione
        title_label = QLabel("Inserisci i nomi dei giocatori")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        player_input_layout.addWidget(title_label)
        
        # Input giocatori affiancati
        players_row = QHBoxLayout()
        players_row.setSpacing(30)
        
        # Giocatore 1
        player1_group = QVBoxLayout()
        player1_label = QLabel("Giocatore 1")
        player1_label.setStyleSheet("font-size: 18px;")
        player1_label.setAlignment(Qt.AlignCenter)
        self.player1_input = QLineEdit()
        self.player1_input.setPlaceholderText("Nome Giocatore 1")
        self.player1_input.setStyleSheet("font-size: 16px; padding: 8px;")
        player1_group.addWidget(player1_label)
        player1_group.addWidget(self.player1_input)
        players_row.addLayout(player1_group)
        
        # Giocatore 2
        player2_group = QVBoxLayout()
        player2_label = QLabel("Giocatore 2")
        player2_label.setStyleSheet("font-size: 18px;")
        player2_label.setAlignment(Qt.AlignCenter)
        self.player2_input = QLineEdit()
        self.player2_input.setPlaceholderText("Nome Giocatore 2")
        self.player2_input.setStyleSheet("font-size: 16px; padding: 8px;")
        player2_group.addWidget(player2_label)
        player2_group.addWidget(self.player2_input)
        players_row.addLayout(player2_group)
        
        player_input_layout.addLayout(players_row)
        
        # Pulsante inizia partita
        self.start_game_btn = QPushButton("INIZIA PARTITA")
        self.start_game_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px; 
                font-weight: bold; 
                padding: 15px;
                background-color: #0171D3;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0081F5;
            }
        """)
        self.start_game_btn.clicked.connect(self.start_game)
        player_input_layout.addWidget(self.start_game_btn)
        
        # Pulsante partite in sospeso (solo se presenti)
        self.resume_game_btn = QPushButton("Partite in sospeso")
        self.resume_game_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background-color: #334E66;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #40617E;
            }
        """)
        self.resume_game_btn.clicked.connect(self.resume_game_dialog)
        self.resume_game_btn.setVisible(self.has_resumable_games())
        player_input_layout.addWidget(self.resume_game_btn)
        
        self.player_input_widget.setLayout(player_input_layout)
        main_layout.addWidget(self.player_input_widget)
        
        # SEZIONE PUNTEGGIO (inizialmente nascosta)
        self.score_widget = QWidget()
        self.score_widget.setVisible(False)
        score_layout = QVBoxLayout()
        score_layout.setSpacing(20)
        
        # Etichette punteggio
        self.score_info = QLabel()
        self.score_info.setAlignment(Qt.AlignCenter)
        self.score_info.setStyleSheet("font-size: 20px; font-weight: bold;")
        score_layout.addWidget(self.score_info)
        
        # Tabella punteggi
        self.score_table = QTableWidget()
        self.score_table.setColumnCount(4)
        self.score_table.setHorizontalHeaderLabels(["Turno", "Punteggio 1", "Punteggio 2", "Dealer"])
        self.score_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.score_table.setStyleSheet("font-size: 14px;")
        score_layout.addWidget(self.score_table)
        
        # Sezione input punteggi - divisa in due gruppi
        input_scores_layout = QHBoxLayout()
        input_scores_layout.setSpacing(30)
        
        # Gruppo giocatore 1
        self.player1_group = QGroupBox()
        self.player1_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        player1_box_layout = QVBoxLayout()
        
        # Punteggio
        player1_score_label = QLabel("Punteggio")
        player1_score_label.setStyleSheet("font-size: 16px;")
        self.player1_score_input = QLineEdit()
        self.player1_score_input.setStyleSheet("font-size: 16px; padding: 8px;")
        self.player1_score_input.textChanged.connect(self.update_opponent_score)
        player1_box_layout.addWidget(player1_score_label)
        player1_box_layout.addWidget(self.player1_score_input)
        
        # Accusi
        accuse_layout = QGridLayout()
        
        # Counter accusi
        self.player1_accuse_counter = QLabel("0")
        self.player1_accuse_counter.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.player1_accuse_counter.setAlignment(Qt.AlignCenter)
        accuse_layout.addWidget(QLabel("Accusi:"), 0, 0)
        accuse_layout.addWidget(self.player1_accuse_counter, 0, 1)
        
        # Pulsanti accusi
        self.player1_accuse_briscola_btn = QPushButton("Accuso Briscola")
        self.player1_accuse_briscola_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 5px;
                background-color: #15619D;
                color: white;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1B7AC6;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.player1_accuse_briscola_btn.clicked.connect(lambda: self.add_accuse(40, 1, True))
        accuse_layout.addWidget(self.player1_accuse_briscola_btn, 1, 0, 1, 2)
        
        self.player1_accuse_btn = QPushButton("Accuso")
        self.player1_accuse_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 5px;
                background-color: #E0E0E0;
                color: black;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #BDBDBD;
            }
            QPushButton:disabled {
                background-color: #EEEEEE;
                color: #9E9E9E;
            }
        """)
        self.player1_accuse_btn.clicked.connect(lambda: self.add_accuse(20, 1, False))
        accuse_layout.addWidget(self.player1_accuse_btn, 2, 0, 1, 2)
        
        player1_box_layout.addLayout(accuse_layout)
        self.player1_group.setLayout(player1_box_layout)
        input_scores_layout.addWidget(self.player1_group)
        
        # Gruppo giocatore 2
        self.player2_group = QGroupBox()
        self.player2_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        player2_box_layout = QVBoxLayout()
        
        # Punteggio
        player2_score_label = QLabel("Punteggio")
        player2_score_label.setStyleSheet("font-size: 16px;")
        self.player2_score_input = QLineEdit()
        self.player2_score_input.setStyleSheet("font-size: 16px; padding: 8px;")
        self.player2_score_input.textChanged.connect(self.update_opponent_score)
        player2_box_layout.addWidget(player2_score_label)
        player2_box_layout.addWidget(self.player2_score_input)
        
        # Accusi
        accuse_layout2 = QGridLayout()
        
        # Counter accusi
        self.player2_accuse_counter = QLabel("0")
        self.player2_accuse_counter.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.player2_accuse_counter.setAlignment(Qt.AlignCenter)
        accuse_layout2.addWidget(QLabel("Accusi:"), 0, 0)
        accuse_layout2.addWidget(self.player2_accuse_counter, 0, 1)
        
        # Pulsanti accusi
        self.player2_accuse_briscola_btn = QPushButton("Accuso Briscola")
        self.player2_accuse_briscola_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 5px;
                background-color: #15619D;
                color: white;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1B7AC6;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.player2_accuse_briscola_btn.clicked.connect(lambda: self.add_accuse(40, 2, True))
        accuse_layout2.addWidget(self.player2_accuse_briscola_btn, 1, 0, 1, 2)
        
        self.player2_accuse_btn = QPushButton("Accuso")
        self.player2_accuse_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 5px;
                background-color: #E0E0E0;
                color: black;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #BDBDBD;
            }
            QPushButton:disabled {
                background-color: #EEEEEE;
                color: #9E9E9E;
            }
        """)
        self.player2_accuse_btn.clicked.connect(lambda: self.add_accuse(20, 2, False))
        accuse_layout2.addWidget(self.player2_accuse_btn, 2, 0, 1, 2)
        
        player2_box_layout.addLayout(accuse_layout2)
        self.player2_group.setLayout(player2_box_layout)
        input_scores_layout.addWidget(self.player2_group)
        
        score_layout.addLayout(input_scores_layout)
        
        # Pulsanti azioni
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.undo_btn = QPushButton("Annulla Ultimo Punteggio")
        self.undo_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        self.undo_btn.clicked.connect(self.undo_last_score)
        button_layout.addWidget(self.undo_btn)

        self.add_score_btn = QPushButton("Aggiungi Punteggio")
        self.add_score_btn.setStyleSheet("font-size: 16px; padding: 10px; background-color: #2196F3; color: white;")
        self.add_score_btn.clicked.connect(self.add_score)
        button_layout.addWidget(self.add_score_btn)
        
        self.save_btn = QPushButton("Salva Partita")
        self.save_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        self.save_btn.clicked.connect(lambda: self.save_game(finished=False))
        button_layout.addWidget(self.save_btn)
        
        score_layout.addLayout(button_layout)
        
        self.score_widget.setLayout(score_layout)
        main_layout.addWidget(self.score_widget)
    
    def update_opponent_score(self):
        sender = self.sender()  # Ottiene quale campo ha generato il segnale
        try:
            if sender == self.player1_score_input:
                # Se stiamo modificando il punteggio del player1
                if self.player1_score_input.text() == "":
                    self.player2_score_input.clear()
                else:
                    score1 = int(self.player1_score_input.text())
                    if score1 > 120:
                        QMessageBox.warning(self, "Errore", "Il punteggio per turno non può superare 120!")
                        self.player1_score_input.clear()
                        self.player2_score_input.clear()
                        return
                    self.player2_score_input.setText(str(120 - score1))
            elif sender == self.player2_score_input:
                # Se stiamo modificando il punteggio del player2
                if self.player2_score_input.text() == "":
                    self.player1_score_input.clear()
                else:
                    score2 = int(self.player2_score_input.text())
                    if score2 > 120:
                        QMessageBox.warning(self, "Errore", "Il punteggio per turno non può superare 120!")
                        self.player1_score_input.clear()
                        self.player2_score_input.clear()
                        return
                    self.player1_score_input.setText(str(120 - score2))
        except ValueError:
            # Ignora se l'input non è un numero valido
            pass
    
    def add_accuse(self, points, player, is_briscola):
        if is_briscola:
            if self.accuse_briscola_used:
                return
                
            self.accuse_briscola_used = True
            # Disabilita entrambi i pulsanti briscola
            self.player1_accuse_briscola_btn.setEnabled(False)
            self.player2_accuse_briscola_btn.setEnabled(False)
        else:
            if self.accuse_count >= 3:
                return
            self.accuse_count += 1
            if self.accuse_count >= 3:
                # Disabilita entrambi i pulsanti accuso normali
                self.player1_accuse_btn.setEnabled(False)
                self.player2_accuse_btn.setEnabled(False)
        
        if player == 1:
            self.accuse_player1 += points
            self.player1_accuse_counter.setText(str(self.accuse_player1))
        else:
            self.accuse_player2 += points
            self.player2_accuse_counter.setText(str(self.accuse_player2))
        
    def has_resumable_games(self):
        """Controlla se ci sono partite da riprendere"""
        if not os.path.exists(self.games_folder):
            return False
        for file in os.listdir(self.games_folder):
            if file.endswith("_toResume.csv"):
                return True
        return False
    
    def resume_game_dialog(self):
        """Mostra la dialog per selezionare una partita da riprendere"""
        files = [f for f in os.listdir(self.games_folder) if f.endswith("_toResume.csv")]
        if not files:
            QMessageBox.information(self, "Nessuna partita", "Non ci sono partite in sospeso!")
            return
            
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona partita da riprendere",
            self.games_folder,
            "CSV Files (*_toResume.csv)"
        )
        
        if file:
            self.resume_game(file)
    
    def resume_game(self, filename):
        """Riprende una partita salvata"""
        try:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Salta l'header
                
                # Leggi i dati della partita
                rows = list(reader)
                if not rows:
                    raise ValueError("File vuoto")
                
                # Estrai nomi giocatori dal nome file
                base_name = os.path.basename(filename)
                players_part = base_name.split("_vs_")
                self.player1 = players_part[0]
                self.player2 = players_part[1].split("_")[0]
                
                # Carica i punteggi
                self.scores = []
                for row in rows:
                    self.scores.append([int(row[0]), int(row[1]), int(row[2]), row[3]])
                
                # Imposta lo stato corrente
                last_row = rows[-1]
                self.total_player1 = int(last_row[1])
                self.total_player2 = int(last_row[2])
                self.card_dealer_turn = 1 if last_row[3] == self.player1 else 2
                self.card_dealer_turn += 1  # Prossimo dealer
                
                # Nascondi la schermata iniziale e mostra quella di gioco
                self.player_input_widget.setVisible(False)
                self.score_widget.setVisible(True)
                
                # Aggiorna l'interfaccia
                self.player1_group.setTitle(f" {self.player1} ")
                self.player2_group.setTitle(f" {self.player2} ")
                self.update_score_table()
                self.update_score_info()
                self.game_active = True
                
                # Resetta gli accusi per il nuovo turno
                self.reset_accuse()
                
                # Rimuovi il file _toResume
                try:
                    os.remove(filename)
                    self.resume_game_btn.setVisible(self.has_resumable_games())
                except:
                    pass
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare la partita:\n{str(e)}")
    
    def start_game(self):
        self.player1 = self.player1_input.text().strip()
        self.player2 = self.player2_input.text().strip()
        
        if not self.player1 or not self.player2:
            QMessageBox.warning(self, "Attenzione", "Inserisci i nomi di entrambi i giocatori!")
            return
            
        if self.player1 == self.player2:
            QMessageBox.warning(self, "Attenzione", "I nomi dei giocatori devono essere diversi!")
            return
            
        self.player_input_widget.setVisible(False)
        self.score_widget.setVisible(True)
        
        # Aggiorna i titoli dei gruppi con i nomi dei giocatori
        self.player1_group.setTitle(f" {self.player1} ")
        self.player2_group.setTitle(f" {self.player2} ")
        
        # Resetta gli accusi
        self.reset_accuse()
        
        # Resetta i punteggi
        self.scores = []
        self.total_player1 = 0
        self.total_player2 = 0
        self.card_dealer_turn = 1
        
        self.update_score_info()
        self.game_active = True
        
    def update_score_info(self):
        dealer = self.player1 if self.card_dealer_turn % 2 == 1 else self.player2
        self.score_info.setText(
            f"{self.player1}: {self.total_player1}                                        |                                        {self.player2}: {self.total_player2}\n\n"
            f"Dealer: {dealer}"
        )
        
    def add_score(self):
        try:
            score1 = int(self.player1_score_input.text())
            score2 = int(self.player2_score_input.text())
            
            # Verifica che la somma dei punteggi sia 120 (esclusi gli accusi)
            if score1 + score2 != 120:
                QMessageBox.warning(self, "Errore", f"La somma dei punteggi deve essere 120 (attualmente {score1 + score2})!")
                return
                
            # Verifica che nessun punteggio superi 120
            if score1 > 120 or score2 > 120:
                QMessageBox.warning(self, "Errore", "Il punteggio per turno non può superare 120!")
                return
                
        except ValueError:
            QMessageBox.warning(self, "Errore", "Inserisci valori numerici validi per i punteggi!")
            return
            
        # Aggiungi gli accusi al punteggio totale
        self.total_player1 += score1 + self.accuse_player1
        self.total_player2 += score2 + self.accuse_player2
        
        dealer = self.player1 if self.card_dealer_turn % 2 == 1 else self.player2
        self.scores.append([len(self.scores) + 1, self.total_player1, self.total_player2, dealer])
        
        # Aggiorna la tabella
        self.update_score_table()
        
        # Cambia il Dealer per il prossimo turno
        self.card_dealer_turn += 1
        
        # Pulisci i campi di input e resetta gli accusi
        self.player1_score_input.clear()
        self.player2_score_input.clear()
        self.reset_accuse()
        
        # Aggiorna le informazioni
        self.update_score_info()
        
        # Controlla se qualcuno ha vinto
        if self.total_player1 >= 1001 or self.total_player2 >= 1001:
            winner = self.player1 if self.total_player1 >= 1001 else self.player2
            QMessageBox.information(self, "Partita Finita", f"La partita è finita! {winner} ha vinto!")
            self.save_game(finished=True)
            self.game_active = False
            self.return_to_main_screen()
            
    def return_to_main_screen(self):
        """Torna alla schermata principale"""
        self.player_input_widget.setVisible(True)
        self.score_widget.setVisible(False)
        
        # Pulisci i campi di input
        self.player1_input.clear()
        self.player2_input.clear()
        self.player1_score_input.clear()
        self.player2_score_input.clear()
        
        # Aggiorna la visibilità del pulsante partite in sospeso
        self.resume_game_btn.setVisible(self.has_resumable_games())
            
    def undo_last_score(self):
        if not self.scores:
            QMessageBox.warning(self, "Attenzione", "Non ci sono punteggi da annullare!")
            return
            
        last_score = self.scores.pop()
        self.total_player1 = self.scores[-1][1] if self.scores else 0
        self.total_player2 = self.scores[-1][2] if self.scores else 0
        
        # Torna indietro con il Dealer solo se abbiamo annullato l'ultimo punteggio
        if len(self.scores) > 0:
            self.card_dealer_turn = 1 if self.scores[-1][3] == self.player1 else 2
        else:
            self.card_dealer_turn = 1
            
        # Resetta gli accusi (non possiamo sapere quali erano nello stato precedente)
        self.reset_accuse()
        
        self.update_score_table()
        self.update_score_info()
        
    def update_score_table(self):
        self.score_table.setRowCount(len(self.scores))
        for row, score in enumerate(self.scores):
            for col, value in enumerate(score):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.score_table.setItem(row, col, item)
                
    def save_game(self, finished=False):
        """Salva la partita corrente"""
        if not self.scores:
            QMessageBox.warning(self, "Attenzione", "Non ci sono punteggi da salvare!")
            return
            
        # Crea il nome file
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{self.player1}_vs_{self.player2}_{current_date}.csv"
        
        # Aggiungi _toResume se la partita non è finita
        if not finished:
            filename = filename.replace(".csv", "_toResume.csv")
        
        # Assicurati che la cartella esista
        if not os.path.exists(self.games_folder):
            os.makedirs(self.games_folder)
        
        # Percorso completo
        filepath = os.path.join(self.games_folder, filename)
        
        # Controlla se il file esiste già
        counter = 1
        while os.path.exists(filepath):
            filename = f"{self.player1}_vs_{self.player2}_{current_date}_{counter}.csv"
            if not finished:
                filename = filename.replace(".csv", "_toResume.csv")
            filepath = os.path.join(self.games_folder, filename)
            counter += 1
            
        try:
            with open(filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Turno", f"{self.player1} (Punteggio)", f"{self.player2} (Punteggio)", "Giocatore che dà le carte"])
                for score in self.scores:
                    writer.writerow(score)
                    
            if finished:
                QMessageBox.information(self, "Salvataggio Completato", f"Partita salvata in:\n{filepath}")
            else:
                QMessageBox.information(self, "Partita sospesa", f"Partita salvata, puoi riprenderla più tardi:\n{filepath}")
                
            # Aggiorna la visibilità del pulsante partite in sospeso
            self.resume_game_btn.setVisible(self.has_resumable_games())
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore durante il salvataggio:\n{str(e)}")

    def reset_accuse(self):
        """Resetta lo stato degli accusi"""
        self.accuse_briscola_used = False
        self.accuse_count = 0
        self.accuse_player1 = 0
        self.accuse_player2 = 0
        self.player1_accuse_counter.setText("0")
        self.player2_accuse_counter.setText("0")
        
        # Riabilita tutti i pulsanti accuso
        self.player1_accuse_briscola_btn.setEnabled(True)
        self.player2_accuse_briscola_btn.setEnabled(True)
        self.player1_accuse_btn.setEnabled(True)
        self.player2_accuse_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScoreTrackerApp()
    window.show()
    sys.exit(app.exec_())