from django.shortcuts import render, redirect
from .models import Client, Note
from .forms import ClientRegistrationForm, NoteForm, ClientRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

import calendar
from datetime import date
from django.utils import timezone

def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_registration_success')
    else:
        form = ClientRegistrationForm()
    return render(request, 'calendar_app/client_registration.html', {'form': form})

def client_notes(request, client_id):
    client = Client.objects.get(id=client_id)
    notes = Note.objects.filter(client=client)
    return render(request, 'calendar_app/notes.html', {'client': client, 'notes': notes})

def add_note(request, client_id):
    client = Client.objects.get(id=client_id)
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.client = client
            note.save()
            return redirect('client_notes', client_id=client.id)
    else:
        form = NoteForm()
    return render(request, 'calendar_app/add_note.html', {'form': form, 'client': client})


#Calendar
def calendar_view(request):
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    week_num = int(request.GET.get('week', today.isocalendar()[1]))

    cal = calendar.Calendar(firstweekday=0)
    month_days = []
    week_list = []
    for week in cal.monthdatescalendar(year, month):
        week_days = []
        for day in week:
            notes = Note.objects.filter(created_at__date=day)
            week_days.append({
                'day': day.day,
                'date': day,
                'in_month': day.month == month,
                'notes': notes,
            })
        iso_week = week[0].isocalendar()[1]
        is_current_week = iso_week == week_num
        month_days.append({'days': week_days, 'is_current_week': is_current_week, 'iso_week': iso_week})
        week_list.append(iso_week)

    # Week navigation
    week_list = sorted(set(week_list))
    if week_num not in week_list:
        week_num = week_list[0]
    week_idx = week_list.index(week_num)
    prev_week = week_list[week_idx - 1] if week_idx > 0 else week_list[0]
    next_week = week_list[week_idx + 1] if week_idx < len(week_list) - 1 else week_list[-1]

    current_week_obj = next((w for w in month_days if w['iso_week'] == week_num), month_days[0])
    first_day = current_week_obj['days'][0]['date']
    last_day = current_week_obj['days'][-1]['date']
    week_range_str = f"{first_day.strftime('%B')} {first_day.day}-{last_day.day}"


    # Month navigation for desktop
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    day_names = list(calendar.day_abbr)

    return render(request, 'calendar_app/calendar.html', {
        'month_days': month_days,
        'today': today,
        'year': year,
        'month': month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'month_name': calendar.month_name[month],
        'day_names': day_names,
        'week_num': week_num,
        'prev_week': prev_week,
        'next_week': next_week,
        'week_range_str': week_range_str,
    })

# Account registration and login views
def client_register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('calendar')
    else:
        form = ClientRegisterForm()
    return render(request, 'calendar_app/client_register.html', {'form': form})

def client_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('calendar')
    else:
        form = AuthenticationForm()
    return render(request, 'calendar_app/client_login.html', {'form': form})

def custom_logout(request):
    logout(request)
    next_url = request.GET.get('next', '/')
    return redirect(next_url)