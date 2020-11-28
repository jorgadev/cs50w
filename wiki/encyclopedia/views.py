from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from markdown import markdown
from random import choice
from . import util

# Search Form
class SearchForm(forms.Form):
    search = forms.CharField(label='', required=True, widget = forms.TextInput(attrs={'placeholder':'Search Encyclopedia', 'autocomplete':'off'}))

# New Page Form
class NewPage(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'style':'display:block; margin-bottom:1rem;'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'style':'display:block; height:200px;'}))

# Edit Page Form
class EditPage(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'style':'display:block; height:200px;'}))

# If "/" is visited, list of entries will be returned
def index(request):
    form = SearchForm(request.POST)
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": form
    })

# If "/wiki" is visited
def wiki(request, title):
    # If "Edit" was clicked on wiki page
    if request.method == "POST":
        return HttpResponseRedirect(f"{reverse('wiki:edit')}?title={title}")
    form = SearchForm(request.POST)
    # Get data from entry which has name that user inserted after /
    data = util.get_entry(title)
    # If data is None, render error page
    if not data:
        message = "Page not found."
        return error(request, message)
    # With markdown library change data to html and render wiki/entry page
    html = markdown(data)
    return render(request, "encyclopedia/wiki/wiki.html", {
        "title": title,
        "html": html,
        "form": form
    })

# If search is visited via link (GET) or via form submission (POST)
def search(request):
    form = SearchForm(request.POST)
    if request.method == "POST":
        # Create a new form with SearchForm class
        if form.is_valid():
            search = form.cleaned_data["search"]
            return HttpResponseRedirect(f"{reverse('wiki:search')}?search_term={search}")
    else:
        # Create a new form with SearchForm class
        form = SearchForm(request.POST)
        # Assign form input to search_term variable
        search_term = request.GET.get("search_term")
        # If search tearm is in markdown entries redirect to that term
        if search_term in util.list_entries():
            return HttpResponseRedirect(f"wiki/{search_term}")
        # For each entry where search term is substring pass to list which will be presented in HTML as list item
        entries = []
        no_results = ""  
        for entry in util.list_entries():
            if search_term in entry:
                entries.append(entry)
        # If there is no result for search input, "No results" will be printed out
        if len(entries) < 1:
            no_results = "No results."
        return render(request, "encyclopedia/search.html", {
            "form": form,
            "entries": entries,
            "no_results": no_results
        })

# If new "Create New Page" is clicked
def new(request):
    form = SearchForm(request.POST)
    new_page_form = NewPage(request.POST)
    # Check if "Create New Page" is visited by link or is submited
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        # On button click check if same title exists
        if title not in util.list_entries():
            util.save_entry(title, content)
            # Redirect user to new entry's page
            return HttpResponseRedirect(f"wiki/{title}")
        # Return error if page with same title exists
        else:
            message = "Page with same title already exists."
            return error(request, message)
    return render(request, "encyclopedia/new.html", {
        "form":form,
        "new_page_form":new_page_form
    })

# If "Random Page" is clicked
def random(request):
    # Get random value from entries and redirect to that page
    value = choice(util.list_entries())
    return HttpResponseRedirect(f"wiki/{value}")



# If "Edit" is clicked
def edit(request):
    form = SearchForm()
    # Get title from entry where "Edit" was clicked
    title = request.GET.get("title")
    edit_form = EditPage(initial = {"content": util.get_entry(title)})

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        util.save_entry(title, content)
        return HttpResponseRedirect(f"wiki/{title}")

    return render(request, "encyclopedia/edit.html", {
        "form": form,
        "title": title,
        "edit_form": edit_form
    })


# Error page
def error(request, message):
    form = SearchForm()
    return render(request, "encyclopedia/error.html", {
        "form": form,
        "message": message
    })