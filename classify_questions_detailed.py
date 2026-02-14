import csv
import os

input_path = r'E:\Mypython\土地家屋調査士試験\ai解答.csv'
output_path = r'E:\Mypython\土地家屋調査士試験\ai解答_categorized_detailed.csv'

def classify_detailed(question_text, explanation_text):
    full_text = (question_text + " " + explanation_text).replace('\n', ' ')
    q_text = question_text.replace('\n', ' ')
    
    # --- 1. Determine Broad Category (Same as before) ---
    broad_category = "不明"
    
    investigator_keywords = ['土地家屋調査士法', '懲戒', '調査士会', '業務範囲', '調査士の義務', '民間紛争解決手続']
    if any(k in full_text for k in investigator_keywords):
        broad_category = '土地家屋調査士法'
    else:
        civil_keywords = [
            '民法', '物権的請求権', '留置権', '先取特権', '質権', '不法行為', '債務不履行', 
            '解除', '取消', '無効', '意思表示', '代理', '時効取得', '遺言', '親族', '配偶者',
            '共有', '相続', '抵当権', '根抵当権', '地役権', '善意', '悪意'
        ]
        registration_keywords = [
            '登記の申請', '地積測量図', '表題部', '地目', '筆界', '合筆', '分筆', '建物図面', 
            '各階平面図', '床面積', '登記官', '却下', '取下げ', '登録免許税', '管轄登記所'
        ]

        civil_score = sum(q_text.count(k) for k in civil_keywords) * 2
        civil_score += sum(explanation_text.count(k) for k in civil_keywords)
        
        reg_score = sum(q_text.count(k) for k in registration_keywords) * 2
        reg_score += sum(explanation_text.count(k) for k in registration_keywords)
        
        if '判例の趣旨' in q_text or '民法' in q_text:
            broad_category = '民法'
        elif civil_score > reg_score:
            broad_category = '民法'
        else:
            # Registration: Land vs Building
            land_keywords = ['土地', '地目', '地積', '筆界', '分筆', '合筆', '地図', '公図', '座標', '境界', '地番']
            building_keywords = ['建物', '床面積', '種類', '構造', '附属建物', '区分建物', '敷地権', '共用部分', '増築', '滅失', '合体', '家屋番号']
            
            q_land = sum(q_text.count(k) for k in land_keywords)
            q_build = sum(q_text.count(k) for k in building_keywords)
            
            if q_build > q_land:
                broad_category = '不動産登記法（建物）'
            elif q_land > q_build:
                broad_category = '不動産登記法（土地）'
            else:
                # Fallback to full text
                land_score = sum(full_text.count(k) for k in land_keywords)
                building_score = sum(full_text.count(k) for k in building_keywords)
                if building_score > land_score:
                    broad_category = '不動産登記法（建物）'
                else:
                    broad_category = '不動産登記法（土地）'

    # --- 2. Determine Detailed Topic ---
    # Scan for specific keywords and pick the most relevant one.
    # We define a mapping of {Topic: [Keywords...]}
    # The order matters: specific topics checked first vs general ones.
    
    topics_map = {
        # Civil Code Topics
        '物権的請求権': ['物権的請求権', '返還請求', '妨害排除'],
        '共有': ['共有', '持分'],
        '遺言': ['遺言', '自筆証書', '公正証書'],
        '相続': ['相続', '遺産分割', '相続人'],
        '時効取得': ['時効取得', '取得時効', '援用'],
        '抵当権': ['抵当権', '法定地上権'],
        '根抵当権': ['根抵当権'],
        '地役権': ['地役権', '承役地', '要役地'],
        '意思表示': ['意思表示', '錯誤', '詐欺', '強迫', '心裡留保', '虚偽表示'],
        '代理': ['代理', '無権代理', '表見代理'],
        '売買・契約': ['売買', '契約解除', '債務不履行', '手付'],
        '不法行為': ['不法行為', '損害賠償'],
        '隣地使用権': ['隣地使用権'],
        '相隣関係': ['相隣関係', '境界線', '枝'],
        
        # Registration (General/Land)
        '筆界特定': ['筆界特定'],
        '地目': ['地目', '雑種地', '宅地', '山林', '原野', '農地'],
        '地積測量図': ['地積測量図', '座標値', '基本三角点'],
        '地図・公図': ['地図', '公図', '地図訂正'],
        '合筆': ['合筆'],
        '分筆': ['分筆'],
        '土地表題登記': ['表題登記', '土地の表題'],
        '地積更正': ['地積更正'],
        '土地滅失': ['土地の滅失', '海没'],
        
        # Registration (Building)
        '区分建物': ['区分建物', '敷地権', '専有部分', '共用部分', '規約'],
        '建物表題登記': ['建物表題登記', '建物の表題'],
        '建物滅失': ['建物滅失', '建物の滅失'],
        '増築': ['増築'],
        '附属建物': ['附属建物'],
        '合体': ['合体'],
        '建物図面': ['建物図面', '各階平面図'],
        '床面積': ['床面積', '不算入'],
        
        # Investigator Law
        '職責・義務': ['職責', '義務', '会則', '依頼'],
        '懲戒': ['懲戒'],
        '調査士法人': ['調査士法人'],
        'ADR': ['ADR', '民間紛争解決'],
        
        # General Registration Procedures
        '管轄': ['管轄登記所', '管轄転属', '管轄指定'],
        '登録免許税': ['登録免許税', '非課税'],
        '審査請求': ['審査請求'],
        '申請情報': ['申請情報', '添付情報'],
        '電子申請': ['電子申請', '電子署名']
    }
    
    detailed_topic = ""
    # Check distinct keywords in full text
    
    # Better approach: Score each topic
    best_topic = ""
    max_score = 0
    
    for topic, keywords in topics_map.items():
        score = 0
        for kw in keywords:
            score += q_text.count(kw) * 3 # High weight for Q text
            score += explanation_text.count(kw)
        
        if score > max_score and score > 0:
            max_score = score
            best_topic = topic
            
    if not best_topic:
        best_topic = "その他"

    return broad_category, best_topic

def process_csv():
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
        
        q_text = row[2] if len(row) > 2 else ""
        exp_text = row[4] if len(row) > 4 else ""
        
        broad, detailed = classify_detailed(q_text, exp_text)
        
        # If output file already has columns, we need to be careful.
        # Original: [Year, QNo, Question, ShortAns, Explanation] + [Category]?
        # Let's assume input has 5 cols always, and maybe 6 if we ran previous script on it.
        # But wait, input_path is referring to the ORIGINAL 'ai解答.csv' based on my code above.
        # My previous script outputted to 'ai解答_categorized.csv'.
        # The user wants me to add to the file.
        # I should probably read the categorized file to preserve work? 
        # But the logic for broad category is re-implemented here.
        # Let's just create a fresh row with [..., Broad, Detailed]
        
        # Normalize to base columns
        base_row = row[:5] # Keep first 5 cols
        
        base_row.append(broad)
        base_row.append(detailed)
        
        updated_rows.append(base_row)

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(updated_rows)
        print(f"Successfully wrote {len(updated_rows)} rows to {output_path}")
        
        for i in range(min(5, len(updated_rows))):
             print(f"Row {i+1}: {updated_rows[i][1]} -> {updated_rows[i][-2]}, {updated_rows[i][-1]}")
             
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == '__main__':
    process_csv()
