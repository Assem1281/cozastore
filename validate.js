// The submit button
const SUBMIT = $( "#submit" );

// Each of the fields and error message divs
const USERNAME = $( "#username" );

const PASSWORD = $( "#password" );

const CONFIRM = $( "#confirm" );

const EMAIL = $( "#email" );



/**
 * Validates the information in the register form so that
 * the server is not required to check this information.
 */
function validate ( )
{
    let valid = true;
    reset_form ( );




    if ( USERNAME.val() != USERNAME.val().toLowerCase())
    {
        valid = false;
    }

    if ( !CONFIRM.val() || PASSWORD.val() != CONFIRM.val() )
    {
        valid = false;
    }


    // If the form is valid, reset error messages
    if ( valid )
    {
        reset_form ( );
    }
}

// Bind the validate function to the required events.
$(document).ready ( validate );
USERNAME.change ( validate );
PASSWORD.change ( validate );
CONFIRM.change ( validate );
EMAIL.change ( validate );


