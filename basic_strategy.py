class Strategy():
    '''
    Простая стратегия, которая равномерно покупает компании из всего получаемого списка 
    '''

    def portfolio_init(self, start_money, regular_money, money_freq, decision_freq):
        
        if money_freq < 1:
            print('money_freq should be >= 1!')
            raise
        if decision_freq < 1:
            print('decision_freq should be >= 1!')
            raise
        
        self.regular_money = regular_money
        self.regular_money_freq = money_freq  # количество дней для регулярных поступлений 
        self.portfolio = {'cash': start_money}  # текущее состояние портфеля
        self.days_left = self.regular_money_freq
        self.decision_freq = decision_freq
        self.days_to_decision = self.decision_freq


    def init_ticker(self, ticker):
        self.portfolio[ticker] = {'price': 0, 'volume': 0}
    
    def portfolio_update(self, ticker, new_price, new_amount, add):
        add = True if add == 'to_buy' else False
        if ticker not in self.portfolio:
            self.init_ticker(ticker)
        if ticker == 'cash':
            self.portfolio[ticker] += new_amount
        elif add:  # добавляем объем в портфель, перевзвешиваем цену
            cash_spend = new_price * new_amount
            self.portfolio[ticker]['price'] = ((self.portfolio[ticker]['price'] * self.portfolio[ticker]['volume'] + cash_spend) / \
                                               (self.portfolio[ticker]['volume'] + new_amount))
            self.portfolio[ticker]['volume'] += new_amount
            self.portfolio['cash'] -= cash_spend
            if self.portfolio['cash'] < 0:
                print('Negative cash!')
                print(self.portfolio['cash'])
                print(ticker, cash_spend)
                raise
        else:  # продаем, ср. цена та же
            cash_earned = new_price * new_amount
            self.portfolio[ticker]['volume'] -= new_amount
            self.portfolio['cash'] += cash_earned


    def init_decision(self):
        des = {'to_buy': {},
               'to_sell': {}}
        return des 


    def get_decision(self, index, time, state):
        '''
        Сама стратегия. Её можно изменять как угодно
        ''' 
        # FIXME: мб проблема множественного вызова внутри дня

        current_decision = self.init_decision()
        added_money = 0
        self.days_left -= 1  
        self.days_to_decision -= 1
        
        if self.days_left == 0:
            added_money = self.regular_money  # for portfolio value calc
            self.portfolio['cash'] += added_money
            self.days_left = self.regular_money_freq

        # покупаем компании, если возможно
        # докупаю в день денег
        if self.days_to_decision == 0:
            current_money = self.portfolio['cash']
            company_share = current_money / len(state)
            for company, company_state in state.items():  # пробегаем по всем компаниям и записываем решение
                current_decision['to_buy'][company] = company_share  # сколько денег на одну компанию
            self.days_to_decision = self.decision_freq
            
        return current_decision, added_money
 