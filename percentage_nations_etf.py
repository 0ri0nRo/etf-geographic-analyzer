import pandas as pd
import numpy as np
import csv
import os
from io import StringIO
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from datetime import datetime

# Impostazioni per matplotlib
plt.style.use('default')
sns.set_palette("husl")

def manual_csv_parsing(csv_file_path):
    """
    Manual parsing per formati CSV complessi con rimozione delle righe sopra l'header
    
    Args:
        csv_file_path (str): Path al file CSV
    
    Returns:
        pd.DataFrame: DataFrame parsato o None se fallisce
    """
    print("Tentativo di parsing manuale...")
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        try:
            with open(csv_file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Impossibile leggere il file anche per il parsing manuale: {e}")
            return None
    
    # Trova l'header e le righe dati
    data_rows = []
    headers = None
    header_line_index = -1
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Cerca la riga header (contiene "Ticker", "Weight", "Location", etc.)
        if headers is None and any(keyword in line.lower() for keyword in ['ticker', 'weight', 'location', 'name', 'sector']):
            try:
                # Split intelligente considerando le virgole dentro le virgolette
                reader = csv.reader(StringIO(line))
                headers = next(reader)
                # Pulisci gli header da spazi extra
                headers = [h.strip() for h in headers]
                header_line_index = i
                print(f"Header trovato alla riga {i+1}: {headers}")
                continue
            except:
                # Fallback: split semplice
                headers = [col.strip() for col in line.split(',')]
                header_line_index = i
                continue
        
        # Se abbiamo trovato gli header, inizia a parsare i dati dalle righe successive
        if headers is not None and i > header_line_index:
            try:
                reader = csv.reader(StringIO(line))
                row = next(reader)
                if len(row) >= 3:  # Almeno 3 colonne (ticker, weight, location)
                    # Assicurati che la riga abbia lo stesso numero di colonne degli header
                    while len(row) < len(headers):
                        row.append('')
                    data_rows.append(row[:len(headers)])
            except:
                # Prova split semplice come fallback
                try:
                    row = [col.strip() for col in line.split(',')]
                    if len(row) >= 3:
                        # Riempi con stringhe vuote se necessario
                        while len(row) < len(headers):
                            row.append('')
                        data_rows.append(row[:len(headers)])
                except:
                    continue
    
    if headers and data_rows:
        df = pd.DataFrame(data_rows, columns=headers)
        print(f"✓ Parsing manuale riuscito: {len(data_rows)} righe, {len(headers)} colonne")
        return df
    else:
        print("✗ Parsing manuale fallito")
        return None

def skip_csv_header_lines(csv_file_path, lines_to_skip=2):
    """
    Salta le prime N righe del CSV e restituisce un file temporaneo pulito
    
    Args:
        csv_file_path (str): Path al file CSV originale
        lines_to_skip (int): Numero di righe da saltare dall'inizio
    
    Returns:
        str: Path del file temporaneo pulito o None se fallisce
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        try:
            with open(csv_file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Impossibile leggere il file per rimuovere le righe header: {e}")
            return None
    
    # Rimuovi le prime N righe
    cleaned_lines = lines[lines_to_skip:]
    
    # Crea file temporaneo
    temp_file_path = csv_file_path.replace('.csv', '_temp_cleaned.csv')
    
    try:
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        print(f"✓ Righe header rimosse. File temporaneo creato: {temp_file_path}")
        return temp_file_path
    except Exception as e:
        print(f"Errore nella creazione del file temporaneo: {e}")
        return None

def analyze_etf_country_allocation(csv_file_path):
    """
    Analizza l'allocazione geografica di un ETF da file CSV
    
    Args:
        csv_file_path (str): Path al file CSV
    
    Returns:
        tuple: (country_weights, country_percentages, clean_dataframe) or None
    """
    
    df = None
    temp_file_path = None
    
    # Prima prova a rimuovere le prime due righe (Fund Holdings as of, riga vuota)
    print("Rimozione delle prime due righe del CSV...")
    temp_file_path = skip_csv_header_lines(csv_file_path, lines_to_skip=2)
    
    if temp_file_path:
        csv_to_read = temp_file_path
    else:
        csv_to_read = csv_file_path
        print("Impossibile creare file temporaneo, uso file originale")
    
    # Prova diversi approcci di lettura
    try:
        print("Tentativo di lettura file CSV...")
        
        # Opzione 1: CSV standard
        try:
            df = pd.read_csv(csv_to_read, encoding='utf-8')
            print("✓ Lettura riuscita con separatore virgola")
        except:
            # Opzione 2: Separatore punto e virgola
            try:
                df = pd.read_csv(csv_to_read, sep=';', encoding='utf-8')
                print("✓ Lettura riuscita con separatore punto e virgola")
            except:
                # Opzione 3: Separatore tab
                try:
                    df = pd.read_csv(csv_to_read, sep='\t', encoding='utf-8')
                    print("✓ Lettura riuscita con separatore tab")
                except:
                    # Opzione 4: Rilevamento automatico separatore
                    try:
                        df = pd.read_csv(csv_to_read, sep=None, engine='python', encoding='utf-8')
                        print("✓ Lettura riuscita con rilevamento automatico separatore")
                    except:
                        # Opzione 5: Encoding latin + rilevamento automatico
                        try:
                            df = pd.read_csv(csv_to_read, sep=None, engine='python', encoding='latin-1')
                            print("✓ Lettura riuscita con encoding latin-1")
                        except:
                            # Prova parsing manuale come ultima risorsa
                            print("Tutti i metodi standard falliti, provo parsing manuale...")
                            df = manual_csv_parsing(csv_file_path)
                            if df is None:
                                return None
                            
    except Exception as e:
        print(f"Errore generale nella lettura del file: {e}")
        return None
    finally:
        # Pulisci file temporaneo
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print("File temporaneo rimosso")
            except:
                print(f"Impossibile rimuovere file temporaneo: {temp_file_path}")
    
    if df is None:
        return None
        
    # Stampa colonne disponibili per debug
    print("\nColonne disponibili nel CSV:")
    print(df.columns.tolist())
    print(f"\nForma DataFrame: {df.shape}")
    print("\nPrime 3 righe:")
    print(df.head(3))
    
    # Identifica automaticamente le colonne rilevanti
    weight_col = None
    location_col = None
    
    # Cerca colonna peso (weight/peso/%)
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if any(keyword in col_lower for keyword in ['weight', 'peso', '%', 'percent', 'allocation']):
            weight_col = col
            break
    
    # Cerca colonna location/paese
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if any(keyword in col_lower for keyword in ['location', 'country', 'paese', 'nazione', 'region']):
            location_col = col
            break
    
    if weight_col is None or location_col is None:
        print(f"\nATTENZIONE: Impossibile identificare automaticamente le colonne.")
        print(f"Colonna peso trovata: {weight_col}")
        print(f"Colonna location trovata: {location_col}")
        
        # Permetti input manuale
        print("\nColonne disponibili:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")
        
        try:
            weight_idx = int(input("Inserisci indice colonna peso: "))
            location_idx = int(input("Inserisci indice colonna location: "))
            
            weight_col = df.columns[weight_idx]
            location_col = df.columns[location_idx]
        except (ValueError, IndexError):
            print("Selezione colonne non valida")
            return None
    
    print(f"\nUso colonna peso: {weight_col}")
    print(f"Uso colonna location: {location_col}")
    
    # Pulisci i dati
    df_clean = df.dropna(subset=[weight_col, location_col]).copy()
    
    # Converti pesi in numerico (gestisci simboli % e stringhe)
    if df_clean[weight_col].dtype == 'object':
        # Rimuovi simboli % e converti
        df_clean[weight_col] = df_clean[weight_col].astype(str).str.replace('%', '').str.replace(',', '.')
        df_clean[weight_col] = pd.to_numeric(df_clean[weight_col], errors='coerce')
    
    # Rimuovi righe con pesi non validi
    df_clean = df_clean.dropna(subset=[weight_col])
    
    # Normalizza nomi paesi
    df_clean[location_col] = df_clean[location_col].astype(str).str.strip()
    
    # Mapping paesi per nomi simili (estendi se necessario)
    country_mapping = {
        'Korea (South)': 'South Korea',
        'China': 'China',
        'Taiwan': 'Taiwan',
        'India': 'India',
        'Germany': 'Germany',
        'South Africa': 'South Africa',
        'Saudi Arabia': 'Saudi Arabia',
        'Brazil': 'Brazil',
        'United States': 'United States',
        'Japan': 'Japan',
        'United Kingdom': 'United Kingdom'
    }
    
    # Applica mapping
    df_clean['Country_Normalized'] = df_clean[location_col].map(country_mapping).fillna(df_clean[location_col])
    
    # Calcola percentuali per paese
    country_weights = df_clean.groupby('Country_Normalized')[weight_col].sum().sort_values(ascending=False)
    
    # Calcola percentuali
    total_weight = country_weights.sum()
    country_percentages = (country_weights / total_weight * 100).round(2)
    
    return country_weights, country_percentages, df_clean

def create_pdf_report(country_weights, country_percentages, df_clean, output_filename="etf_country_allocation_report.pdf"):
    """
    Crea un report PDF con grafico a torta e tabella
    
    Args:
        country_weights: Serie pandas con i pesi per paese
        country_percentages: Serie pandas con le percentuali per paese
        df_clean: DataFrame pulito
        output_filename: Nome del file PDF di output
    """
    
    with PdfPages(output_filename) as pdf:
        # Pagina 1: Grafico a torta
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 16))
        
        # Prepara i dati per il grafico a torta
        # Raggruppa i paesi con meno del 2% in "Altri"
        threshold = 2.0
        main_countries = country_percentages[country_percentages >= threshold]
        other_countries = country_percentages[country_percentages < threshold]
        
        if len(other_countries) > 0:
            plot_data = main_countries.copy()
            plot_data['Altri'] = other_countries.sum()
        else:
            plot_data = country_percentages.copy()
        
        # Grafico a torta
        colors = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))
        wedges, texts, autotexts = ax1.pie(plot_data.values, 
                                          labels=plot_data.index,
                                          autopct='%1.1f%%',
                                          startangle=90,
                                          colors=colors)
        
        # Migliora la leggibilità
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=9)
        
        ax1.set_title('Allocazione Geografica ETF', fontsize=16, fontweight='bold', pad=20)
        
        # Tabella dettagliata
        ax2.axis('tight')
        ax2.axis('off')
        
        # Prepara dati per la tabella
        table_data = []
        table_data.append(['Paese', 'Peso Totale', 'Percentuale'])
        
        for country in country_percentages.index:
            weight = country_weights[country]
            percentage = country_percentages[country]
            table_data.append([country, f'{weight:.2f}', f'{percentage:.2f}%'])
        
        # Aggiungi riga totale
        table_data.append(['TOTALE', f'{country_weights.sum():.2f}', f'{country_percentages.sum():.2f}%'])
        
        # Crea tabella
        table = ax2.table(cellText=table_data[1:],
                         colLabels=table_data[0],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.4, 0.3, 0.3])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        # Stilizza l'header
        for i in range(len(table_data[0])):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Stilizza le righe alternate
        for i in range(1, len(table_data)):
            for j in range(len(table_data[0])):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#F2F2F2')
        
        # Stilizza la riga totale
        last_row = len(table_data) - 1
        for j in range(len(table_data[0])):
            table[(last_row, j)].set_facecolor('#D9E1F2')
            table[(last_row, j)].set_text_props(weight='bold')
        
        ax2.set_title('Dettaglio Allocazione per Paese', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Pagina 2: Statistiche aggiuntive
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8))
        
        # Grafico a barre orizzontali - Top 10 paesi
        top_10 = country_percentages.head(10)
        bars = ax1.barh(range(len(top_10)), top_10.values)
        ax1.set_yticks(range(len(top_10)))
        ax1.set_yticklabels(top_10.index)
        ax1.set_xlabel('Percentuale (%)')
        ax1.set_title('Top 10 Paesi per Allocazione')
        ax1.invert_yaxis()
        
        # Aggiungi valori sulle barre
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}%', ha='left', va='center', fontsize=8)
        
        # Istogramma distribuzione pesi
        ax2.hist(country_percentages.values, bins=20, edgecolor='black', alpha=0.7)
        ax2.set_xlabel('Percentuale (%)')
        ax2.set_ylabel('Numero di Paesi')
        ax2.set_title('Distribuzione delle Allocazioni')
        
        # Box plot
        ax3.boxplot(country_percentages.values, vert=True)
        ax3.set_ylabel('Percentuale (%)')
        ax3.set_title('Box Plot delle Allocazioni')
        ax3.set_xticklabels(['Tutti i Paesi'])
        
        # Statistiche testuali
        ax4.axis('off')
        stats_text = f"""
STATISTICHE RIASSUNTIVE

Totale holdings: {len(df_clean)}
Numero di paesi: {len(country_percentages)}

CONCENTRAZIONE:
Top 3 paesi: {country_percentages.head(3).sum():.2f}%
Top 5 paesi: {country_percentages.head(5).sum():.2f}%
Top 10 paesi: {country_percentages.head(10).sum():.2f}%

DISTRIBUZIONE:
Media: {country_percentages.mean():.2f}%
Mediana: {country_percentages.median():.2f}%
Dev. Standard: {country_percentages.std():.2f}%

ESTREMI:
Max allocazione: {country_percentages.iloc[0]:.2f}% ({country_percentages.index[0]})
Min allocazione: {country_percentages.iloc[-1]:.2f}% ({country_percentages.index[-1]})

Report generato: {datetime.now().strftime("%d/%m/%Y %H:%M")}
        """
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"✓ Report PDF creato: {output_filename}")

def print_results(country_weights, country_percentages):
    """Stampa risultati in formato leggibile"""
    
    print("\n" + "="*60)
    print("ALLOCAZIONE GEOGRAFICA ETF")
    print("="*60)
    
    print(f"\n{'Paese':<25} {'Peso Totale':<15} {'Percentuale':<15}")
    print("-" * 60)
    
    for country in country_percentages.index:
        weight = country_weights[country]
        percentage = country_percentages[country]
        print(f"{country:<25} {weight:<15.2f} {percentage:<15.2f}%")
    
    print("-" * 60)
    print(f"{'TOTALE':<25} {country_weights.sum():<15.2f} {country_percentages.sum():<15.2f}%")
    
    # Top 5 paesi
    print(f"\nTOP 5 PAESI:")
    for i, (country, percentage) in enumerate(country_percentages.head(5).items(), 1):
        print(f"{i}. {country}: {percentage:.2f}%")

def export_results(country_weights, country_percentages, output_file="country_allocation.csv"):
    """Esporta risultati in CSV"""
    
    results_df = pd.DataFrame({
        'Country': country_percentages.index,
        'Total_Weight': country_weights.values,
        'Percentage': country_percentages.values
    }).sort_values('Percentage', ascending=False)
    
    results_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nRisultati esportati in: {output_file}")
    return results_df

# Esecuzione principale
if __name__ == "__main__":
    # Sostituisci con il path del tuo file CSV
    csv_file = "weqw_holdings.csv"
    
    print("Script di Analisi Allocazione Geografica ETF")
    print("=" * 50)
    
    # Controlla se il file esiste, chiedi all'utente altrimenti
    if not os.path.exists(csv_file):
        csv_file = input("Inserisci il path del file CSV: ").strip('"\'')
        if not os.path.exists(csv_file):
            print(f"File non trovato: {csv_file}")
            exit(1)
    
    print(f"Analizzando file: {csv_file}")
    
    # Analizza il file
    result = analyze_etf_country_allocation(csv_file)
    
    if result:
        country_weights, country_percentages, df_clean = result
        
        # Stampa risultati
        print_results(country_weights, country_percentages)
        
        # Esporta risultati CSV
        export_results(country_weights, country_percentages)
        
        # Crea report PDF
        try:
            create_pdf_report(country_weights, country_percentages, df_clean)
            print("✓ Report PDF creato con successo!")
        except Exception as e:
            print(f"Errore nella creazione del PDF: {e}")
            print("Assicurati di avere installato matplotlib: pip install matplotlib")
        
        # Statistiche aggiuntive
        print(f"\nSTATISTICHE:")
        print(f"Totale holdings: {len(df_clean)}")
        print(f"Numero di paesi: {len(country_percentages)}")
        print(f"Concentrazione top 3 paesi: {country_percentages.head(3).sum():.2f}%")
        print(f"Concentrazione top 5 paesi: {country_percentages.head(5).sum():.2f}%")
        
        # Analisi concentrazione
        if len(country_percentages) > 1:
            print(f"Paese più concentrato: {country_percentages.iloc[0]:.2f}%")
            print(f"Paese meno concentrato: {country_percentages.iloc[-1]:.2f}%")
        
    else:
        print("\n" + "="*60)
        print("IMPOSSIBILE ANALIZZARE IL FILE")
        print("="*60)
        print("Suggerimenti:")
        print("1. Controlla che il file sia un CSV valido")
        print("2. Assicurati che contenga colonne 'Weight' e 'Location'")
        print("3. Prova a salvare il file come CSV UTF-8 da Excel")
        print("4. Controlla caratteri speciali negli header")
        print("5. Assicurati che il path del file sia corretto")
        
        # Mostra info file per debug
        try:
            with open(csv_file, 'r') as f:
                first_lines = [next(f) for _ in range(min(3, sum(1 for _ in f) + 1))]
                print(f"\nPrime righe del file:")
                for i, line in enumerate(first_lines, 1):
                    print(f"Riga {i}: {repr(line[:100])}")  # Mostra primi 100 caratteri
        except Exception as e:
            print(f"Impossibile leggere il file anche per debug: {e}")

print("\n" + "="*60)
print("Script completato!")
print("="*60)
