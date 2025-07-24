from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .fynk import search_cell_start, search_cell_end, app_data, terminal, model_search, excel_load_terminal_add
from Alfa_repair_app.models import Batch, SerialNumber
from django.template.loader import render_to_string


def login_views(request):
    return render(request, 'login.html')


def login_aut(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return render(request, 'home.html')
    else:
        return render(request, 'login.html', {'error': 'Invalid username or password'})


def out(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def index(request):
    return render(request, 'home.html')


@login_required(login_url='login')
def add_bank_req(request):
    if request.method == 'POST' and request.FILES['excel']:
        city = request.POST.get('city', '').strip()
        model_cell_start = search_cell_start('Номенклатура', 'C8:C12', request.FILES['excel'])
        sn_cell_start = search_cell_start('Серийный номер', 'D8:D12', request.FILES['excel'])
        model_cell_end = search_cell_end(3, sn_cell_start, request.FILES['excel'])
        sn_cell_end = search_cell_end(4, model_cell_start, request.FILES['excel'])
        if model_cell_start is False:
            return JsonResponse({"success": False, "error": 'Не удалось получить индексы старта строки модель'})
        elif sn_cell_start is False:
            return JsonResponse({"success": False, "error": 'Не удалось получить индексы старта строки СН'})
        elif model_cell_end is False:
            return JsonResponse({"success": False, "error": 'Не удалось получить индексы конца строки модель'})
        elif sn_cell_end is False:
            return JsonResponse({"success": False, "error": 'Не удалось получить индексы конца строки СН'})
        range_model = f'C{model_cell_start + 1}:C{model_cell_end}'
        range_sn = f'D{sn_cell_start + 1}:D{sn_cell_end}'
        data_excel = app_data(range_model, range_sn, request.FILES['excel'])
        if data_excel:
            last_number = Batch.objects.order_by('-created_at').values_list('number', flat=True).first()
            if last_number is None:
                last_number = 1
            else:
                last_number += 1
            batch, created = Batch.objects.get_or_create(
                number=last_number,
                defaults={"city": city},
            )

            serial_objects = [
                SerialNumber(batch=batch, serial=sn, model_bank=model, status='Ожидает принятия')
                for sn, model in data_excel
            ]

            SerialNumber.objects.bulk_create(serial_objects)
            return JsonResponse({"success": True, 'data_excel': data_excel})
    return render(request, 'add_bank_req.html')


@login_required(login_url='login')
def acceptance(request):
    if request.method == 'GET':
        req = Batch.objects.filter(status='acceptance')
        req_data = [(i.number, i.city) for i in req]
        return render(request, 'acceptance.html', {'req_data': req_data})
    if request.method == 'POST':
        number_req = request.POST['number']
        request.session['number_req'] = number_req
        return redirect('acceptance_terminal')


def acceptance_terminal(request):
    number_req = request.session.get('number_req')
    met = request.POST.get('source')
    if not number_req:
        return JsonResponse({"success": False, "message": "Партия не выбрана."})

    try:
        part_number, city = number_req.split(',')
        part = Batch.objects.get(number=part_number, city=city)
    except (ValueError, Batch.DoesNotExist):
        return JsonResponse({"success": False, "message": "Некорректные данные о партии."})

    if request.method == "POST":
        serial = request.POST.get("serial", "").strip()
        if met == 'manual':
            if not serial:
                return JsonResponse({"success": False, "message": "Серийный номер не указан."})

            try:
                sn = SerialNumber.objects.get(serial=serial, batch=part)
                if sn.status == "Принят":
                    return JsonResponse({"success": False, "message": f"Серийный номер '{serial}' уже принят."})
                if model_search(sn.model_bank):
                    model_brand = model_search(sn.model_bank)
                    sn.status = "Принят"
                    sn.model = model_brand['model']
                    sn.brand = model_brand['brand']
                    sn.save()
                else:
                    return JsonResponse({
                        "success": False,
                        "message": f"Серийный номер '{serial}' не найден в выбранной партии."
                    })

            except SerialNumber.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": f"Серийный номер '{serial}' не найден в выбранной партии."})
        elif met == 'excel':
            excel_file = request.FILES.get("excel_file")
            excel_load_terminal_add(excel_file, part_number, city)
            return JsonResponse({"success": True})

        # Обновим отображение таблиц
        terminal_data = terminal(part_number)
        html = render_to_string("partials/serial_tables.html", {
            "accepted": terminal_data['accepted'],
            'accepted_count': terminal_data['accepted_count'],
            "not_accepted": terminal_data['not_accepted'],
            "not_accepted_count": terminal_data['not_accepted_count'],
        })

        return JsonResponse({"success": True, "html": html, "message": f"Серийный номер '{serial}' принят."})

    # GET-запрос
    terminal_data = terminal(part_number)
    context = {
        'number_req': part_number,
        'city': city,
        'count_terminal': terminal_data['serial_count'],
        "accepted": terminal_data['accepted'],
        'accepted_count': terminal_data['accepted_count'],
        "not_accepted": terminal_data['not_accepted'],
        "not_accepted_count": terminal_data['not_accepted_count'],
    }
    return render(request, 'acceptance_terminal.html', context)
