from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction
from .forms import TransactionForm
from dashboard.decorators import allowed_users 
from .models import Credit, Debit, TransactionHistory, FinanceSummary
from .forms import CreditForm, DebitForm, TransactionHistoryForm, FinanceSummaryForm

#user bank management
@login_required
def account_dashboard(request):
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-transaction_date')
    return render(request, 'account_dashboard.html', {'account': account, 'transactions': transactions})

@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = Account.objects.get(user=request.user)
            transaction.save()
            return redirect('account_dashboard')
    else:
        form = TransactionForm()

    return render(request, 'create_transaction.html', {'form': form})


#System bank management

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance'])
def credit_list(request):
    credits = Credit.objects.all() 
    if(credits):
        print('yes')
    context = {
        'credits': credits,
    }
    return render(request, 'finance/credit_list.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance'])
def debit_list(request):
    debits = Debit.objects.all()
    context = {
        'debits': debits,
    }
    return render(request, 'finance/debit_list.html', context)



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance'])
def transaction_history(request):
    transactions = TransactionHistory.objects.all().order_by('-date')
    is_finance = request.user.groups.filter(name='Finance').exists() 
    context = {
        'transactions': transactions,
        'is_finance':is_finance
    }
    return render(request, 'finance/transaction_history.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance'])
def finance_summary(request):
    summaries = FinanceSummary.objects.all().order_by('-date')
    context = {
        'summaries': summaries,
    }
    return render(request, 'finance/finance_summary.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance'])
def add_credit(request):
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('credit_list')
    else:
        form = CreditForm()
    return render(request, 'finance/add_credit.html', {'form': form})


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance'])
def add_debit(request):
    if request.method == 'POST':
        form = DebitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('debit_list')
    else:
        form = DebitForm()
    return render(request, 'finance/add_debit.html', {'form': form})


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance'])
def add_transaction_history(request):
    if request.method == 'POST':
        form = TransactionHistoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_history')
    else:
        form = TransactionHistoryForm()
    return render(request, 'finance/add_transaction_history.html', {'form': form})


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Finance'])
def add_finance_summary(request):
    if request.method == 'POST':
        form = FinanceSummaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('finance_summary')
    else:
        form = FinanceSummaryForm()
    return render(request, 'finance/add_finance_summary.html', {'form': form})

