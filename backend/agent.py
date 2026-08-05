"""
================================================================================
AI AGENT - EXPENSE CATEGORIZATION AGENT
WITH OLLAMA LLM INTEGRATION
================================================================================
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Tuple

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama not installed. Run: pip install ollama")

# ============================================================
# MEMORY CACHE (RAG)
# ============================================================

class MemoryCache:
    def __init__(self, filepath='memory_cache.json'):
        self.filepath = filepath
        self.data = self.load()
    
    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, merchant):
        merchant_lower = merchant.lower()
        if merchant_lower in self.data:
            return self.data[merchant_lower]['category'], self.data[merchant_lower]['confidence']
        return None, 0
    
    def set(self, merchant, category, confidence):
        merchant_lower = merchant.lower()
        self.data[merchant_lower] = {
            'category': category,
            'confidence': confidence,
            'last_used': datetime.now().isoformat()
        }
        self.save()
    
    def get_stats(self):
        return {
            'total_entries': len(self.data),
            'categories': list(set([v['category'] for v in self.data.values()]))
        }

# ============================================================
# MAIN AGENT
# ============================================================

class ExpenseCategorizationAgent:
    """Multi-Strategy AI Agent: Rules + Memory + LLM"""
    
    def __init__(self):
        self.categories = {
    'food': [
        'restaurant', 'cafe', 'coffee', 'breakfast', 'lunch', 'dinner',
        'pizza', 'burger', 'food', 'grocery', 'meal', 'eat', 'dining',
        'swiggy', 'zomato', 'domino', 'kfc', 'mcd', 'macdonald',
        'pizza hut', 'burger king', 'subway', 'taco bell',
        'starbucks', 'costa', 'cafe coffee day', 'barista',
        'dmart', 'bigbasket', 'grofers', 'zepto', 'instamart',
        'reliance fresh', 'fresh', 'bazaar', 'supermarket',
        'amazon fresh', 'uber eats', 'swiggy genie',
        'meal', 'lunch', 'dinner', 'breakfast', 'snack'
    ],
    
    'shopping': [
        'amazon', 'flipkart', 'snapdeal', 'meesho', 'shopclues',
        'myntra', 'ajio', 'nykaa', 'trends', 'clothing', 'fashion',
        'electronics', 'gadget', 'mobile', 'laptop', 'computer',
        'reliance digital', 'apple store', 'croma', 'vijay sales',
        'mall', 'mart', 'shop', 'store', 'supermarket', 'retail',
        'market', 'shopping', 'online', 'ecommerce'
    ],
    
    'entertainment': [
        'netflix', 'amazon prime', 'prime video', 'hotstar', 'disney',
        'hulu', 'hbomax', 'peacock', 'sonyliv', 'zee5', 'voot',
        'spotify', 'apple music', 'youtube music', 'gaana', 'wynk',
        'music', 'song', 'playlist',
        'movie', 'cinema', 'theatre', 'bookmyshow', 'pvr', 'inox',
        'game', 'gaming', 'playstation', 'xbox', 'nintendo',
        'entertainment', 'event', 'concert', 'show', 'comedy'
    ],
    
    'health': [
        'hospital', 'clinic', 'doctor', 'dentist', 'eye', 'cardio',
        'medicine', 'pharmacy', 'drug', 'prescription',
        'apollo', 'medplus', 'netmeds', '1mg', 'pharmeasy',
        'apollo pharmacy', 'medlife',
        'gym', 'fitness', 'yoga', 'workout', 'exercise', 'training',
        "gold's gym", 'cult', 'snap fitness',
        'star health', 'health insurance', 'medical insurance',
        'wellness', 'vitamin', 'supplement', 'nutrition'
    ],
    
    'transport': [
        'uber', 'ola', 'lyft', 'uber cab', 'ola cab',
        'train', 'bus', 'metro', 'subway', 'tram',
        'petrol', 'diesel', 'fuel', 'gas', 'cnp', 'toll',
        'taxi', 'cab', 'auto', 'rickshaw', 'bike', 'car',
        'uber freight', 'freight', 'logistics', 'delivery'
    ],
    
    'bills': [
        'electricity', 'water', 'gas', 'bill', 'utility', 'municipal',
        'phone', 'mobile', 'recharge', 'airtel', 'jio', 'vi', 'bsnl',
        'reliance jio', 'jio fiber', 'broadband', 'wifi',
        'internet', 'network', 'data', 'broadband',
        'cloud', 'icloud', 'google drive', 'onedrive', 'dropbox',
        'rent', 'maintenance', 'society', 'apartment', 'housing',
        'subscription', 'premium', 'membership'
    ],
    
    'education': [
        'udemy', 'coursera', 'edx', 'udacity', 'skillshare',
        'linkedin learning', 'pluralsight', 'great learning',
        'book', 'kindle', 'amazon kindle', 'read', 'library',
        'ebook', 'audiobook', 'audible',
        'college', 'university', 'school', 'class', 'course',
        'certificate', 'degree', 'diploma',
        'education', 'learn', 'study', 'tution'
    ],
    
    'travel': [
        'flight', 'airline', 'air india', 'indigo', 'spicejet',
        'vistara', 'akasa', 'goair', 'booking', 'cancellation',
        'flight booking', 'flight cancellation',
        'hotel', 'resort', 'stay', 'lodging', 'accommodation',
        'oyo', 'airbnb', 'booking.com', 'makemytrip',
        'travel', 'trip', 'vacation', 'tour', 'holiday',
        'railway', 'irctc', 'bus booking', 'taxi service'
    ],
    
    'salary': [
        'salary', 'payroll', 'wages', 'income', 'credit',
        'payment', 'remuneration', 'pay', 'earnings'
    ],
    
    'other': []
    }
        
        self.memory = MemoryCache()
        self.categorized = []
        self.uncategorized = []
        self.iteration_log = []
        self.max_iterations = 50
        self.total_transactions = 0
        self.memory_hits = 0
        self.rule_hits = 0
        self.llm_hits = 0
        self.ollama_model = 'llama3.2'
    
    def tool_read_csv(self, csv_file: str) -> List[Dict]:
        print(f"\n📂 Reading {csv_file}...")
        transactions = []
        
        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    transaction = {
                        'date': row.get('date', ''),
                        'description': row.get('description', row.get('name', '')),
                        'amount': float(row.get('amount', row.get('value', 0))),
                        'category': 'uncategorized',
                        'confidence': 0.0
                    }
                    transactions.append(transaction)
            
            print(f"✅ Read {len(transactions)} transactions")
            self.total_transactions = len(transactions)
            return transactions
            
        except FileNotFoundError:
            print(f"❌ File '{csv_file}' not found!")
            return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    # ============================================================
    # MULTI-STRATEGY CATEGORIZATION: Memory → Rules → LLM
    # ============================================================
    
    def tool_categorize_with_llm(self, description: str) -> Tuple[str, float]:
        """
        Multi-Strategy Decision Pipeline:
        1. Memory (RAG) - Instant recall of learned patterns
        2. Smart Rules - Fast path for clear matches
        3. AI Contextual Understanding (Ollama) - Intelligent reasoning for complex cases
        """
        print(f"   🔍 Analyzing: '{description}'")
        
        # STEP 1: RAG MEMORY - Fastest, 100% accurate for learned patterns
        category, confidence = self.memory.get(description)
        if category:
            self.memory_hits += 1
            print(f"   ✅ PATTERN RECALL: {category} ({confidence:.0%})")
            return category, confidence
        
        # STEP 2: SMART RULES - Fast path for clear, unambiguous merchants
        desc = description.lower()
        rule_matches = []
        
        for cat, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in desc:
                    rule_matches.append((cat, keyword))
        
        # SINGLE CLEAR MATCH - Use Rules (Fast)
        if len(rule_matches) == 1:
            cat, keyword = rule_matches[0]
            confidence = 0.85
            self.rule_hits += 1
            self.memory.set(description, cat, confidence)
            print(f"   ✅ PATTERN MATCH: {cat} (85%)")
            return cat, confidence
        
        # MULTIPLE MATCHES - Use AI for Contextual Understanding
        elif len(rule_matches) > 1:
            print(f"   🔄 Multiple patterns found: {len(rule_matches)}")
            print(f"   🧠 Using AI for contextual understanding...")
            category, confidence = self.tool_llm_categorize(description)
            if category != 'other' and confidence > 0.6:
                self.llm_hits += 1
                self.memory.set(description, category, confidence)
                print(f"   ✅ AI UNDERSTANDING: {category} ({confidence:.0%})")
                return category, confidence
        
        # NO MATCH - Use AI for Intelligent Reasoning
        else:
            print(f"   🧠 Using AI for intelligent reasoning...")
            category, confidence = self.tool_llm_categorize(description)
            if category != 'other' and confidence > 0.6:
                self.llm_hits += 1
                self.memory.set(description, category, confidence)
                print(f"   ✅ AI UNDERSTANDING: {category} ({confidence:.0%})")
                return category, confidence
        
        # FALLBACK - Safe default
        self.memory.set(description, 'other', 0.3)
        print(f"   ✅ FALLBACK: other (30%)")
        return 'other', 0.3
    
    # ============================================================
    # AI CONTEXTUAL UNDERSTANDING (Ollama)
    # ============================================================
    
    def tool_llm_categorize(self, description: str) -> Tuple[str, float]:
        """
        Uses Ollama LLM for contextual understanding of complex cases.
        Handles ambiguity, new merchants, and brand context.
        """
        if not OLLAMA_AVAILABLE:
            return 'other', 0.3
        
        try:
            categories = ['food', 'transport', 'shopping', 'bills', 'entertainment', 
                         'health', 'education', 'salary', 'travel', 'other']
            
            prompt = f'''Analyze this expense description and categorize it.

Description: "{description}"

Categories: {", ".join(categories)}

Consider:
- Brand context (Amazon Fresh = grocery, Uber Eats = food delivery)
- Product/service type
- Common industry classification

Reply with ONLY the category name, nothing else.'''
            
            print(f"   🤖 AI Analysis in progress...")
            
            response = ollama.chat(
                model=self.ollama_model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            category = response['message']['content'].strip().lower()
            
            if category in categories:
                return category, 0.90
            else:
                for cat in categories:
                    if cat in category:
                        return cat, 0.75
                return 'other', 0.5
                
        except Exception as e:
            print(f"   ❌ AI Error: {e}")
            return 'other', 0.3
    
    # ============================================================
    # GENERATE REPORT
    # ============================================================
    
    def tool_generate_report(self):
        category_counts = {}
        total_spent = 0
        
        for txn in self.categorized:
            cat = txn['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
            total_spent += txn['amount']
        
        mem_stats = self.memory.get_stats()
        
        report = {
            'generated': datetime.now().isoformat(),
            'total_transactions': self.total_transactions,
            'total_spent': total_spent,
            'categories': category_counts,
            'categorized_count': len(self.categorized),
            'uncategorized_count': len(self.uncategorized),
            'memory_stats': mem_stats,
            'memory_hits': self.memory_hits,
            'rule_hits': self.rule_hits,
            'llm_hits': self.llm_hits,
            'accuracy': (self.memory_hits + self.rule_hits + self.llm_hits) / self.total_transactions if self.total_transactions > 0 else 0,
            'ollama_available': OLLAMA_AVAILABLE
        }
        
        with open('expense_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    # ============================================================
    # AGENT LOOP: Perceive → Plan → Act → Observe
    # ============================================================
    
    def perceive(self, csv_file: str) -> List[Dict]:
        print("\n👁️ PERCEIVE: Reading input...")
        return self.tool_read_csv(csv_file)
    
    def plan(self, transactions: List[Dict]) -> Dict:
        print("\n🧠 PLAN: Deciding next action...")
        for txn in transactions:
            if txn['category'] == 'uncategorized':
                return {'action': 'categorize', 'transaction': txn}
        return {'action': 'complete'}
    
    def act(self, transaction: Dict) -> Dict:
        print(f"\n⚡ ACT: Processing '{transaction['description']}'...")
        category, confidence = self.tool_categorize_with_llm(transaction['description'])
        transaction['category'] = category
        transaction['confidence'] = confidence
        return transaction
    
    def observe(self, transaction: Dict, iteration: int):
        print(f"\n👀 OBSERVE: Logging iteration {iteration}")
        
        log_entry = {
            'iteration': iteration,
            'transaction': transaction['description'],
            'category': transaction['category'],
            'confidence': transaction['confidence'],
            'timestamp': datetime.now().isoformat()
        }
        
        self.iteration_log.append(log_entry)
        
        if transaction['category'] != 'uncategorized':
            self.categorized.append(transaction)
        else:
            self.uncategorized.append(transaction)
        
        with open('iteration_log.json', 'w') as f:
            json.dump(self.iteration_log, f, indent=2)
    
    def is_complete(self, transactions: List[Dict]) -> bool:
        for txn in transactions:
            if txn['category'] == 'uncategorized':
                return False
        return True
    
    def run(self, csv_file: str):
        print("\n" + "="*60)
        print("🤖 MULTI-STRATEGY AI AGENT")
        print("   Memory → Smart Rules → AI Understanding")
        print("="*60)
        
        transactions = self.perceive(csv_file)
        if not transactions:
            return
        
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 ITERATION {iteration}")
            print(f"{'='*60}")
            
            decision = self.plan(transactions)
            if decision['action'] == 'complete':
                print("\n✅ All transactions categorized!")
                break
            
            transaction = self.act(decision['transaction'])
            
            for i, txn in enumerate(transactions):
                if txn['description'] == transaction['description']:
                    transactions[i] = transaction
            
            self.observe(transaction, iteration)
            
            if self.is_complete(transactions):
                print("\n✅ SUCCESS: All transactions categorized!")
                break
        
        self.tool_generate_report()
        
        print("\n" + "="*60)
        print("📊 FINAL SUMMARY")
        print("="*60)
        print(f"Total Transactions: {self.total_transactions}")
        print(f"Categorized: {len(self.categorized)}")
        print(f"Uncategorized: {len(self.uncategorized)}")
        print(f"Iterations used: {iteration}")
        print(f"Memory entries: {len(self.memory.data)}")
        print(f"Ollama Available: {OLLAMA_AVAILABLE}")
        print(f"LLM Hits: {self.llm_hits}")
        print("\n✅ Logs saved to iteration_log.json")
        print("✅ Report saved to expense_report.json")
        print("✅ Memory saved to memory_cache.json")