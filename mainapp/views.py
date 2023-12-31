from django.http.response import HttpResponse
from django.shortcuts import render
from yahoo_fin.stock_info import *
import time
import queue
from threading import Thread
from asgiref.sync import sync_to_async

# Create your views here.
def stockPicker(request):
    stock_picker = tickers_nifty50()
    #print(stock_picker)
    return render(request, 'mainapp/stockpicker.html', {'stockpicker':stock_picker})

@sync_to_async
def checkAuthenticated(request):
    if not request.user.is_authenticated:
        return False
    else:
        return True

async def stockTracker(request):
    is_loginned = await checkAuthenticated(request)
    if not is_loginned:
        return HttpResponse("Login First")
    # stockpicker = request.POST.getlist('stockpicker')
    stockpicker = request.GET.getlist('stockpicker')
    print(stockpicker)
    data = {}
    available_stocks = tickers_nifty50()
    for i in stockpicker:
        if i in available_stocks:
            pass
        else:
            return HttpResponse("Error")
    start = time.time()    
    # for i in stockpicker:
    #     details = get_quote_table(i)
    #     data.update({i: details})    
    
    n_threads = len(stockpicker)
    thread_list = []
    que = queue.Queue()
    for i in range(n_threads):
        thread = Thread(target = lambda q, arg1: q.put({stockpicker[i]: get_quote_table(arg1)}), args = (que, stockpicker[i]))
        thread_list.append(thread)
        thread_list[i].start()
    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)    
    end = time.time()
    time_taken =  end - start
    # print(data)
    print(time_taken)
    return render(request,'mainapp/stocktracker.html',{'data': data , 'room_name': 'track'})    