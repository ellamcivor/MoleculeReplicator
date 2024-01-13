/* javascript to accompany jquery.html */

$(document).ready( 
  /* this defines a function that gets called after the document is in memory */
  function()
  {

    /* go to molecule page */
    $("#mol_view").click(
        function()
      {
        window.location.href = "mol_view.html";
      }
    );


    /* go to element page */
    $("#element_view").click(
        function()
      {
        window.location.href = "element_view.html";
      }
    );


    /* submit element data */
    $("#add_elements").click(function() {

        var formData = {
            status: "add",
            number: $("#in_number").val(),
            symbol: $("#in_symbol").val(),
            name: $("#in_name").val(),
            c1: $("#in_c1").val(),
            c2: $("#in_c2").val(),
            c3: $("#in_c3").val(),
            radius: $("#in_rad").val()
        };

        $.ajax({
            url: "/element_view.html",
            method: 'POST',
            data: formData,
            success: function(response) {
                window.location.href = window.location.pathname;
            },
            error: function(data, status) {
                alert(data.responseText);
            }
        });
    });



    /* submit element data */
    $("#rem_elements").click(
        function()
        {
    
    $.post("/element_view.html",
    
      {
        status: "remove",
        element_code: $(".selected").find(".e_code").text()
      },
      function( )
      {
        window.location.href = window.location.pathname;
      }
    )

        }
    )


    /* go to sdf_upload page */
    $("#sdf_upload").click(
        function()
      {
        window.location.href = "sdf_upload.html";
      }
    );


    /* upload sdf file data */
    $("#sdf_submit").click(function() {
 
        var formData = {
            filename: $("#sdf_file").val(),
            name: $("#mol_name").val()
        };

        $.ajax({
            url: '/sdf_upload.html',
            method: 'POST',
            data: formData,
            success: function(response) {
                // Redirect to a new page if successful
                window.location.href = '/mol_view.html';
            },
            error: function(data, status) {
                // Display error message
                alert(data.responseText);
            }
        });
    });


     /* go to svg_view page */
    $("#mol_display").click(
        function()
        {
    
    $.post("/svg_view.html",
    
      {
        status: "view",
        molname: $(".selected").find(".m_name").text()
      },
      function( )
      {
        window.location.href = "svg_view.html";
      }
    );

        }
    );


    /* rotate molecule */
    $("#rotate").click(function() {

        var formData = {
            status: "rotate",
            x: $("#x_rot").val(),
            y: $("#y_rot").val(),
            z: $("#z_rot").val()
        };

        $.ajax({
            url: "/svg_view.html",
            method: 'POST',
            data: formData,
            success: function(response) {
                window.location.href = window.location.pathname;
            },
            error: function(data, status) {
                alert(data.responseText);
            }
        });
    });


    $(".row").mouseenter(function() {
        highlight(this);
    });

    $(".row").mouseleave(function() {
        unHighlight(this);
    });

    $(".row").click(function() {
        select(this);
    });

    function highlight( row )
    {
        $(row).addClass("highlighted");
    }

    function unHighlight( row )
    {
        $(row).removeClass("highlighted");
    }

    function select( row )
    {
        $(".row").removeClass("selected");
        $(row).addClass("selected");
        $("#rem_elements").removeClass("invisible");
        $("#rem_elements").addClass("light_pink");
        $("#mol_display").removeClass("invisible");
        $("#mol_display").addClass("light_pink");
    }
  }
);
