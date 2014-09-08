from django.shortcuts import render
from django.http import HttpResponse
from BucketList.models import BucketListItem, UserProfile
from django.contrib import auth
from forms import BucketListItemForm, UserProfileForm, UserProfileEditForm, BucketListItemEditForm, CustomItemEditForm
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required



def index(request):
    """The main Bucket List Page View, sorted by pubdate so the most recent are at the top"""
    all_list_items = BucketListItem.objects.all().order_by('-pub_date')
    
    context = {'all_list_items': all_list_items}
    
    return render(request, 'BucketList/index.html', context)
    
    
def index_items(request, id):
    """When a user clicks on a Bucket List Item on the index page it will take them here with a brief overview of that items information"""
    item = BucketListItem.objects.all().filter(pk = id)
    context = {'item': item[0],
                      'id': id,
                    }
    return render(request, 'BucketList/index_items.html', context)
    
    
@login_required
def user_stats(request, id):
    """A public stats/profile page that displays their basic profile information as well as their bucket list"""
    item = User.objects.all().filter(username = id)
    item_profile = item[0].userprofile
    list_of_all = BucketListItem.objects.all().filter(pub_by = item)
    context = {'id': id,
                      'item': item[0],
                      'list_of_all': list_of_all,
                      'item_profile': item_profile,
                    }
    return render(request, 'BucketList/user_stats.html', context)
    

@login_required
def index_stats(request):
    """This page compiles interesting statistics about all of the Bucket List Items on the main index page and displays that information"""
    list_of_all = BucketListItem.objects.all().count()
    total_cost = BucketListItem.objects.all().aggregate(Sum('cost'))
    total_time = BucketListItem.objects.all().aggregate(Sum('time'))
    total_crossed_off = BucketListItem.objects.all().aggregate(Sum('crossed_off'))
    number_of_users = User.objects.all().count()
    cost_per_user = total_cost['cost__sum']/number_of_users
    time_per_user = total_time['time__sum']/number_of_users
    items_per_user = list_of_all/number_of_users
    crossed_off_per_user = total_crossed_off['crossed_off__sum']/number_of_users
    
    context = {'list_of_all': list_of_all,
                      'total_cost': total_cost['cost__sum'],
                      'total_time': total_time['time__sum'],
                      'total_crossed_off': total_crossed_off['crossed_off__sum'],
                      'crossed_off_per_user': crossed_off_per_user,
                      'number_of_users': number_of_users,
                      'cost_per_user': cost_per_user,
                      'time_per_user': time_per_user,
                      'items_per_user': items_per_user,
                      }
                      
    return render(request, 'BucketList/index_stats.html', context)
    
    
@login_required
def my_list(request):
    """The current users personal Bucket List view with links to create more list items or learn statistics about their list"""
    personal_list = BucketListItem.objects.all().filter(pub_by = request.user.id)
    
    context = {'personal_list': personal_list,
                      'user': request.user.username
                    }
                      
    return render(request, 'BucketList/mylist.html', context)
    
    
@login_required
def recommendation(request):
    """This view takes the users list items and turns it into a convenient display of the stats in a user friendly form, basically this view is the main reason everything else in this web app exists. """
    user = UserProfile.objects.get(pk = request.user.id)
    mylist = BucketListItem.objects.all().filter(pub_by = user)
    total_cost = mylist.aggregate(Sum('cost'))
    total_hours = mylist.aggregate(Sum('hours'))
    total_time = mylist.aggregate(Sum('time'))
    total_number_of_items = int(len(mylist))
    age = user.age

    need_to_accomplish_per_year_70 = total_number_of_items/(70 - int(user.age))
    
    if need_to_accomplish_per_year_70 < 1:
        need_to_accomplish_per_year_70 = 1

    context = {'user': user,
                     'mylist': mylist,
                     'total_cost': total_cost['cost__sum'],
                     'total_hours': total_hours['hours__sum'],
                     'total_time': total_time['time__sum'],
                     'total_number_of_items': total_number_of_items,
                     'need_to_accomplish_per_year_70': need_to_accomplish_per_year_70,
                    }
                    
    return render(request, 'BucketList/recommendation.html', context)
    
    
    
@login_required
def my_list_stats(request):
    """General statistics about the current users Bucket List"""
    personal_list = BucketListItem.objects.all().filter(pub_by = request.user.id)
    total_cost = BucketListItem.objects.all().filter(pub_by = request.user.id).aggregate(Sum('cost'))
    total_time = BucketListItem.objects.all().filter(pub_by = request.user.id).aggregate(Sum('time'))
    total_crossed_off = BucketListItem.objects.all().filter(pub_by = request.user.id).aggregate(Sum('crossed_off'))
    cost_per_list_item = total_cost['cost__sum']/personal_list.count()
    time_per_list_item = total_time['time__sum']/personal_list.count()
    
    context = {'personal_list': personal_list,
                      'user': request.user.username,
                      'total_cost': total_cost['cost__sum'],
                      'total_time': total_time['time__sum'],
                      'total_crossed_off': total_crossed_off['crossed_off__sum'],
                      'cost_per_list_item': cost_per_list_item,
                      'time_per_list_item': time_per_list_item,
                      }
                      
    return render(request, 'BucketList/my_list_stats.html', context)
    
    
@login_required
def view_my_list_item(request, id):
    """View of a current users Bucket List Item with options to cross off or edit the Bucket List Item"""
    logged_in = request.user.id
    item = BucketListItem.objects.filter(pk = id)
    context = {'logged_in': logged_in,
                      'item': item[0],
                    }
    return render(request, 'BucketList/view_my_list_item.html', context)
    
@login_required
def cross_off_my_list_item(request, id):
    """The view that crosses off the Bucket List Item"""
    item = BucketListItem.objects.get(pk = id)
    item.crossed_off = True
    item.pub_date = timezone.now()
    item.save()
    
    context = {'item': item,
                      'User': User,
                    }
    return render(request, 'BucketList/crossed_off.html', context)
    
    
    
@login_required
def uncross_my_list_item(request, id):
    """The view that uncrosses off the Bucket List Item"""
    item = BucketListItem.objects.get(pk = id)
    item.crossed_off = False
    item.pub_date = timezone.now()
    item.save()
    
    context = {'item': item,
                      'User': User,
                    }
    return render(request, 'BucketList/uncross.html', context)
    
    
 
@login_required
def delete_my_list_item(request, id):
    """The view that uncrosses off the Bucket List Item"""
    item = BucketListItem.objects.get(pk = id)
    title = item.text
    item.delete()
    
    context = {'title': title,
                      'User': User,
                    }
    return render(request, 'BucketList/delete.html', context)
    
    
    
@login_required
def create(request):
    """Creates a Bucket List Item, the user only fills out the Name and Type of the item while the rest of the fields are auto-filled: publication date, published by, crossed off, time, hours, and cost """
    if request.POST:
        form = BucketListItemForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            my_model = form.save(commit = False)
            my_model.pub_by = user
            my_model.crossed_off = False
            my_model.time = 0
            my_model.hours = 0
            my_model.cost = 0
            my_model.save()
            return HttpResponseRedirect('/bucketlist/create/%s' % my_model.id)
    else:
        form = BucketListItemForm()
            
    args = {}
    args.update(csrf(request))
    args['form'] = form
        
    return render_to_response('BucketList/create_item.html', args)
    

@login_required
def create_specific_item(request, id):
    """Taken here immediately after creating the bucket list item, takes user to a specific view based upon what goal type they input and then gives them another form to give more detail about the goal"""
    item1 = BucketListItem.objects.all().filter(pk = id)
    item2 = item1[0]
    goal_type = item2.goal_type
    
    if goal_type == 'Travel':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_time = form.cleaned_data['new_time']
                new_cost = form.cleaned_data['new_cost']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})    
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/travel.html', args)
    
        
    elif goal_type == 'Purchase':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/purchase.html', args)

        
    elif goal_type == 'Career':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/career.html', args)
        
        
    elif goal_type == 'Extreme Sport':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/extremesport.html', args)
        
        
    elif goal_type == 'Family/Social':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/familysocial.html', args)
        
        
    elif goal_type == 'Relationship':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/relationship.html', args)
        
        
    elif goal_type == 'Exercise/Health':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/exercisehealth.html', args)
        
    elif goal_type == 'Improving a Skill':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/improveskill.html', args)
        
    elif goal_type == 'Hobby':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/hobby.html', args)
        
    elif goal_type == 'Building/Creating Somthing':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/buildcreate.html', args)
        
        
    elif goal_type == 'Education/Self Improvement':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/education.html', args)
        
        
    elif goal_type == 'Volunteering':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/volunteering.html', args)    
        
    elif goal_type == 'Other':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/other.html', args)    
    
                
                
@login_required
def edit_profile(request):
    """A view that allows the user to edit their current profile information"""
    current_user = UserProfile.objects.get(pk = request.user.id)
    if request.method == "POST":
        form = UserProfileEditForm(request.POST)
        if form.is_valid():
            new_age = form.cleaned_data['new_age']
            new_life_expectancy = form.cleaned_data['new_life_expectancy']
            current_user.life_expectancy = new_life_expectancy
            current_user.age = new_age   
            current_user.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
    else:
        form = UserProfileEditForm({'new_age': current_user.age, 'new_life_expectancy': current_user.life_expectancy})
        
    return render(request, 'BucketList/edit_user_profile.html', {'form': form})
    
    
@login_required
def edit_bucket_list_item(request, id):
    """This view lets the user edit their Bucket List Item and directs them to other forms necessary to make the changes needed"""
    item = BucketListItem.objects.get(pk = id)
    if request.method == "POST":
        form = BucketListItemEditForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            goal_type = form.cleaned_data['goal_type']
            item.text = text
            item.goal_type = goal_type
            item.pub_date = timezone.now()
            item.save()
            return HttpResponseRedirect('/bucketlist/create/%s' % item.id)
    else:
        form = BucketListItemEditForm({'text': item.text, 'goal_type': item.goal_type})
        
    return render(request, 'BucketList/edit_bucket_list_item.html', {'form': form, 'id': item.id})
    
    
        