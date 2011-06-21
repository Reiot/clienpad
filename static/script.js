function render_post(board, post){
	var html = '<li>'
	+ post.author
	+ '<a href="/' + board + '/' + post.id + '">' 
	+ post.title 
	+ '<span class="ui-li-aside ui-li-desc">' + post.publish_time_short + '</span>'
	+ '</a>';
	if(post.comment_count>0){
		html += '<span class="ui-li-count">' + post.comment_count + '</span>';
	}					
	html += '</li>';					
	return html;
}

function render_image_post(board, post){
	var html = 
	'<li data-role="list-divider">' +
	    post.author +
	    '<h2>' + post.title + '</h2>' +
	    '<span class="ui-li-aside ui-li-desc">' + post.info + '</span>' +		
	'</li>' +
	'<li>' +
		'<div>' + post.content + '</div>';
		
	if(post.comments.length){
		html += '<div><ul data-role="listview" data-inset="true">';
		var i;
		for(i = 0 ; i < post.comments.length ; i ++ ){
		    var comment = post.comments[i];
			html += '<li>' + comment.author + comment.content + '</li>';
		}
		html += '</ul></div>';
	}
	html += '</li>';
	return html;
	//var $html = $(html).find('ul[data-role="listview"]').listview();
	//return $html;
}

function add_post(board, $posts, data){
	var i;
	for( i = 0 ; i < data.length ; i ++ ){
		var li;
		if(board==="image"){
		    li = render_image_post(board, data[i]);
		}else{
            li = render_post(board, data[i]);
		}
		$posts.append(li);
	}
	$posts.listview('refresh');	
}

$(function(){
	
	$('a.refresh').live('vclick', function(){
		var $button = $(this),
			board = $button.data('board');
			
		console.log('board', board);
		
		var $posts = $button.parents('div[data-role="page"]').find('ul.posts');
		$posts.empty();

		$.mobile.showPageLoadingMsg();

		$.getJSON("/"+board, { format: "json" })
			.success(function(response){
				console.log('response',response);
				add_post(board, $posts, response.posts);
			})
			.complete(function(){
				$.mobile.hidePageLoadingMsg();
			});
	});
	
	$('a.more').live('vclick', function(e){
		var $button = $(this),
			board = $button.data('board'),
			nextPage = $button.data('next-page');
			
		console.log(e.type, 'board', board, 'nextPage', nextPage);		
		
		var $posts = $button.parents('div[data-role="page"]').find('ul.posts');		
		$.mobile.showPageLoadingMsg();
		
        $button.attr("disabled","disabled");
		$.getJSON("/"+board+"/page"+nextPage, { format: "json" })
			.success(function(response){
				console.log('response',response);
				add_post(board, $posts, response.posts);
				$button.data('next-page', response.next_page);
				
				if(board==="image"){
				    var $li = $posts.find("li");
				    if($li.size() > 16){
				        $posts.find("li:lt(4)").remove();
				    }
				}
			})
			.complete(function(){
                $.mobile.hidePageLoadingMsg();
				//$.mobile.silentScroll(100);	
                $button.attr("disabled","");
			});
	});
});