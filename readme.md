# Instructions

## Essential Objects:
### Creating an admin user - Done
### Customers table Declaration - Done
### Customers table Constructor - Done
### Creating a customer - active/inactive column - Done
### Books table Declaration - Done
### Books table Constructor - Done
### Creating a book - active/inactive column - Done
### Loans table Declaration - Done
Loans table Constructor

## Register page
Front page
### Registering a new user
### Message of successful resgister
### Message of user exists
Link back to Login page

## Login page
Front Page
### Valid details
### Wrong user
### Wrong Password
### Inactive user
Links to books page after login

## ---ADMIN----------------------------------------------------------------------------
### Menu: Books, customers, loans, Logout
### Books page:
Front page
#### Add a book - Done
No image file was chosen case
Display all books:
 - All details
 - Delete button
#### Find book by name
Search query is done with the existence of sub-string
Option to cancel the search
#### Remove a book
1. Getting the id of the book
2. if the book is loaned, killing the loan first --> then removing
3. Actually changes the book to inactive ("ERASED")
### Customer page:
Front page
#### Display all customers:
- All details
- Delete button
#### Remove customers
Only customers with no loans are removable
No actually deleting - changing status to inactive
#### Find customer by name:
Search query is done with the existence of sub-string
Option to cancel the search
### Loans page
Details of every active and inactive loan
Option to show only late loans
## ---USER----------------------------------------------------------------------------
### Menu: Books, loans, Logout
### Books page
#### Loan a book:
1. Create a new loan
2. Change book's status to LOANED
3. Other users will not see this book in the list
4. The loan will appear in the loans page with a return button
### Loans page
#### List of loans with details
#### Return a book:
1. Change in loans table the row to inactive
2. Change the book status to AVAILABLE
3. The book will return to the list
#### Filter to late loans only


### subtelties
Redirection and links to pages
admin: id=1 
