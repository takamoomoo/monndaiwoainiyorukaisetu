import csv
import os

input_path = r'E:\Mypython\土地家屋調査士試験\ai解答.csv'
output_path = r'E:\Mypython\土地家屋調査士試験\ai解答_categorized.csv'

def classify(question_text, explanation_text):
    # Combine but prioritize question text
    full_text = (question_text + " " + explanation_text).replace('\n', ' ')
    q_text = question_text.replace('\n', ' ')
    
    # Priority 1: 土地家屋調査士法
    # Strong keywords usually found in the question or specific explanation context
    investigator_keywords = ['土地家屋調査士法', '懲戒', '調査士会', '業務範囲', '調査士の義務', '民間紛争解決手続']
    if any(k in full_text for k in investigator_keywords):
        return '土地家屋調査士法'

    # Priority 2: 民法 (Civil Code)
    # Civil Code questions (usually Q1-3) focus on Rights, Validity, etc.
    civil_keywords = [
        '民法', '物権的請求権', '留置権', '先取特権', '質権', '不法行為', '債務不履行', 
        '解除', '取消', '無効', '意思表示', '代理', '時効取得', '遺言', '親族', '配偶者',
        '共有', '相続', '抵当権', '根抵当権', '地役権', '善意', '悪意'
    ]
    
    # Registration Law keywords
    registration_keywords = [
        '登記の申請', '地積測量図', '表題部', '地目', '筆界', '合筆', '分筆', '建物図面', 
        '各階平面図', '床面積', '登記官', '却下', '取下げ', '登録免許税', '管轄登記所'
    ]

    civil_score = sum(q_text.count(k) for k in civil_keywords) * 2  # Weight question text higher
    civil_score += sum(explanation_text.count(k) for k in civil_keywords)
    
    reg_score = sum(q_text.count(k) for k in registration_keywords) * 2
    reg_score += sum(explanation_text.count(k) for k in registration_keywords)
    
    # Heuristic for Q1-Q3 (often Civil Code)
    # If "民法" or "判例" is explicitly mentioned in Question, it's Civil Code.
    if '判例の趣旨' in q_text or '民法' in q_text:
        return '民法'

    if civil_score > reg_score:
        return '民法'
    
    # If Registration Law, distinguish Land vs Building
    land_keywords = ['土地', '地目', '地積', '筆界', '分筆', '合筆', '地図', '公図', '座標', '境界', '地番']
    building_keywords = ['建物', '床面積', '種類', '構造', '附属建物', '区分建物', '敷地権', '共用部分', '増築', '滅失', '合体', '家屋番号']
    
    # Check Question text first for decisive subject
    q_land = sum(q_text.count(k) for k in land_keywords)
    q_build = sum(q_text.count(k) for k in building_keywords)
    
    if q_build > q_land:
        return '不動産登記法（建物）'
    elif q_land > q_build:
        return '不動産登記法（土地）'

    # Fallback to full text scoring
    land_score = sum(full_text.count(k) for k in land_keywords)
    building_score = sum(full_text.count(k) for k in building_keywords)

    if building_score > land_score:
        return '不動産登記法（建物）'
    
    return '不動産登記法（土地）'

def process_csv():
    # Detect encoding (defaulting to utf-8 based on previous success)
    encoding = 'utf-8'
    
    rows = []
    try:
        with open(input_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    updated_rows = []
    
    for row in rows:
        if not row: continue
        # Assuming Row structure: [Year, QNo, Question, ShortAns, Explanation, (Category?)]
        # We append to the end.
        if len(row) >= 5:
            q_text = row[2]
            exp_text = row[4]
            category = classify(q_text, exp_text)
            
            # If re-running, replace the last column if it looks like a category?
            # User said "Add a column", so we append.
            # But if I run this locally multiple times, I don't want to keep appending.
            # Check if last column is already a valid category.
            valid_cats = ['民法', '不動産登記法（土地）', '不動産登記法（建物）', '土地家屋調査士法']
            if row[-1] in valid_cats:
                row[-1] = category # Update existing
            else:
                row.append(category) # Append new
        
        updated_rows.append(row)

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(updated_rows)
        print(f"Successfully wrote {len(updated_rows)} rows to {output_path}")
        
        # Validation output
        for i in range(min(5, len(updated_rows))):
             print(f"Row {i+1}: {updated_rows[i][1]} -> {updated_rows[i][-1]}")
             
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == '__main__':
    process_csv()
