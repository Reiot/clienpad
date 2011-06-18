function render_post(board, post){
	var html = '<li>'
	+ post.author
	+ '<a href="/' + board + '/' + post.id + '">' 
	+ post.title 
	+ '<span class="ui-li-aside ui-li-desc">' + post.publish_time_short + '</span>'
	+ '</a>';
	if(post.comments>0){
		html += '<span class="ui-li-count">' + post.comments + '</span>';
	}					
	html += '</li>';					
	return html;
}

function render_image_post(board, post){
	var html = 
	'<li data-role="list-divider">' +
	    post.author +
	    '<h2>' + post.title + '</h2>' +
	'</li>' +
	'<li>' +
		'<div>' + post.content + '</div>';
		
	if(post.comments.length){
		html += '<ul data-role="listview" data-inset="true">';
		var i;
		for(i = 0 ; i < post.comments.length ; i ++ ){
		    var comment = post.comments[i];
			html += '<li>' + comment.author + comment.content + '</li>';
		}
		html += '</ul>';
	}
	html += '</li>';
	return html;
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
	
	$('a.refresh').live('click', function(){
		var $button = $(this),
			board = $button.data('board');
			
		console.log('board', board);
		
		var $posts = $button.parents('div[data-role="page"]').find('ul.posts');
		$posts.empty();

		$.mobile.pageLoading();

		$.getJSON("/"+board, { format: "json" })
			.success(function(response){
				console.log('response',response);
				add_post(board, $posts, response.posts);
			})
			.complete(function(){
				$.mobile.pageLoading(true);
			});
	});
	
	$('a.more').live('click', function(){
		var $button = $(this),
			board = $button.data('board'),
			nextPage = $button.data('next-page');
			
		console.log('board', board, 'nextPage', nextPage);
		
		var $posts = $button.parents('div[data-role="page"]').find('ul.posts');		
		$.mobile.pageLoading();
		
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
				$.mobile.pageLoading(true);
				//$.mobile.silentScroll(100);	
			});
	});
});