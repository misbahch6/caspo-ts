clc

for k=1:100
	for i=1:126
		for j=12:32
			BT20(i,j)=rand(1);
		end
    end

    BT20b=dataset({BT20,headerRow{:}});
    filename=sprintf('test%d.csv', k);
    export(BT20b,'File',filename,'Delimiter',',')

end
