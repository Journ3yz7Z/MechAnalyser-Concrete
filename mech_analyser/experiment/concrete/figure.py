"""170 x 103 mm publication overlay; display changes never alter regression."""
import numpy as np
from .presentation import band, clear_box, parameter_rows


def export_figure(a, path, xlim=None):
    import matplotlib as mpl
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.offsetbox import TextArea, HPacker, VPacker, DrawingArea, AnnotationBbox
    from matplotlib.lines import Line2D
    from matplotlib.transforms import ScaledTranslation
    from .collation import AXIAL, HOOP
    with mpl.rc_context({'font.family':['Times New Roman','SimSun'], 'font.size':9,
                         'axes.unicode_minus':False, 'mathtext.fontset':'custom',
                         'mathtext.rm':'Times New Roman', 'mathtext.it':'Times New Roman:italic',
                         'mathtext.bf':'Times New Roman:bold', 'mathtext.fallback':'stix'}):
        fig=Figure(figsize=(170/25.4,103/25.4),dpi=600)
        FigureCanvasAgg(fig)
        ax=fig.add_subplot(111)
        fig.subplots_adjust(left=.075,right=.98,bottom=.16,top=.975)
        f,s,r=a.raw_data.frame,a.selected,a.result
        valid=f.valid.to_numpy()
        for key,color,label in [('axial',AXIAL,'轴向应变'),('hoop',HOOP,'横向应变')]:
            ax.plot(np.where(valid,f[key],np.nan),np.where(valid,f.stress,np.nan),color=color,lw=1.3,label=label,zorder=3)
            fit=r.get('E' if key == 'axial' else 'kh')
            if fit and len(s):
                xx=np.array([s[key].min(),s[key].max()])
                ax.plot(xx,fit['intercept']+fit['slope']*xx,color='#c62828',lw=1.3,ls='-',zorder=4)
        xs=np.concatenate([f.axial[valid],f.hoop[valid],[0.]])
        xmin,xmax=float(np.nanmin(xs)),float(np.nanmax(xs))
        dx=max(xmax-xmin,1e-6)
        xmin,xmax=xmin-.04*dx,xmax+.10*dx
        peak=r.get('peak_stress_MPa',1.)
        ax.set_xlim(*(xlim if xlim is not None else (xmin,xmax)))
        ax.set_ylim(min(0,float(f.stress[valid].min())),max(peak*1.22,1.))
        ax.spines['left'].set_position(('data',0))
        for name in ('left','bottom'):
            ax.spines[name].set_linewidth(1.)
        for name in ('right','top'):
            ax.spines[name].set_visible(False)
        ax.set_xlabel('应变',fontsize=10,fontweight='bold',labelpad=8)
        ax.set_ylabel('应力(MPa)',fontsize=10,fontweight='bold')
        ax.yaxis.set_label_coords(0,.5,transform=ax.transAxes+ScaledTranslation(-7/72,0,fig.dpi_scale_trans))
        ax.yaxis.label.set_verticalalignment('bottom')
        ax.tick_params(labelsize=9,width=.8,length=3.75,pad=3)
        ax.minorticks_off()
        ax.grid(color='#e0e0e0',lw=.35)
        ax.set_axisbelow(True)
        m=a.metadata
        val=lambda k:str(m.get(k,'')).strip() or '未填写'
        labels,values=zip(*parameter_rows(a))
        def text(t,size=9,**kw):
            return TextArea(t,textprops=dict(fontsize=size,fontfamily=['Times New Roman','SimSun'],**kw))
        label_column=VPacker(children=[text(label) for label in labels],align='left',pad=0,sep=1.35)
        value_column=VPacker(children=[text('：'+value) for value in values],align='left',pad=0,sep=1.35)
        table=HPacker(children=[label_column,value_column],align='top',pad=0,sep=0)
        info=VPacker(children=[text(m.get('test_type') or '单轴压缩试验',9.5),table],align='left',pad=0,sep=1.35)
        info_artist=AnnotationBbox(info,(0,1),xycoords='axes fraction',xybox=(8,-8),
                                    boxcoords='offset points',box_alignment=(0,1),frameon=False,pad=0)
        ax.add_artist(info_artist)
        handles=[Line2D([],[],color=c,lw=1.3,label=l) for c,l in
                 [(AXIAL,'轴向应变'),(HOOP,'横向应变'),('#c62828','拟合曲线')]]
        legend=ax.legend(handles=handles,loc='upper left',bbox_to_anchor=(.64 if xlim is not None else .36,.965),fontsize=9.5,frameon=False,
                  handlelength=23/9.5,handletextpad=5/9.5,borderpad=0,borderaxespad=0,labelspacing=.4)
        bounds=band(a)
        result_artist=band_text=None
        if bounds:
            lo,hi=bounds
            ax.axhspan(lo,hi,color='#58799b',alpha=.07,zorder=0)
            for v in bounds:
                ax.axhline(v,color='#7890a8',lw=.65,zorder=1)
            center=(lo+hi)/2
            band_text=ax.text(.42,center,'线性弹性区间',transform=ax.get_yaxis_transform(),
                    ha='left',va='bottom',fontsize=9,color='#4371a8')
            result_rows=[]
            if 'E_GPa' in r:
                result_rows.append(text(r'$E = '+f'{r["E_GPa"]:.3f}'+r'\ \mathrm{GPa}$'))
            if r.get('nu') is not None:
                rule=DrawingArea(18,1)
                rule.add_artist(Line2D([0,18],[.5,.5],lw=.55,color='black'))
                denominator=HPacker(children=[text(r'$k$'),text('横',6.5)],align='bottom',pad=0,sep=0)
                fraction=VPacker(children=[text(r'$E$'),rule,denominator],align='center',pad=0,sep=0)
                result_rows.append(HPacker(children=[text(r'$\nu = -$'),fraction,text(f' = {r["nu"]:.3f}')],
                                           align='center',pad=0,sep=1.5))
            if result_rows:
                result_block=VPacker(children=result_rows,align='left',pad=0,sep=2)
                result_artist=AnnotationBbox(result_block,(.51,center),xycoords=ax.get_yaxis_transform(),
                                            box_alignment=(0,0),frameon=False,pad=0)
                ax.add_artist(result_artist)
                result_artist.set_gid('fit-results')
        px=r.get('peak_axial_strain')
        peak_visible=px is not None and ax.get_xlim()[0]<=px<=ax.get_xlim()[1]
        if px is not None:
            if peak_visible:
                ax.plot([px],[peak],marker='o',ms=5.5,mec='none',color='#e02020',ls='none',zorder=5)
                peak_text=ax.annotate(r'$f_c = '+f'{peak:.3f}'+r'\ \mathrm{MPa}$',xy=(px,peak),xytext=(12,12),
                                     textcoords='offset points',ha='left',va='bottom',fontsize=9)
            else:
                peak_text=ax.text(.62,.67,r'$f_c = '+f'{peak:.3f}'+r'\ \mathrm{MPa}$'+'\n峰值位于显示范围外',transform=ax.transAxes,fontsize=9)
        fig.canvas.draw()
        if px is not None and xlim is None:
            renderer=fig.canvas.get_renderer()
            overflow=peak_text.get_window_extent(renderer).x1-(fig.bbox.x1-4*fig.dpi/72)
            if overflow>0:
                current=ax.get_xlim()
                fraction=(px-current[0])/(current[1]-current[0])
                target=max(.35,fraction-(overflow+2*fig.dpi/72)/ax.bbox.width)
                ax.set_xlim(current[0],current[0]+(px-current[0])/target)
        fig.canvas.draw()
        if info_artist is not None:
            renderer=fig.canvas.get_renderer()
            b=info_artist.get_window_extent(renderer)
            size=(b.width/ax.bbox.width,b.height/ax.bbox.height)
            preferred=(.025,.52-size[1]/2) if xlim is not None else (.025,.975-size[1])
            obstacles=[]
            if xlim is None:
                for item in [legend]+([peak_text] if px is not None else []):
                    rect=item.get_window_extent(renderer).transformed(ax.transAxes.inverted())
                    obstacles.append((rect.x0,rect.y0,rect.x1,rect.y1))
            place=clear_box(a,(ax.get_xlim(),ax.get_ylim()),size,preferred,obstacles)
            if place is not None:
                info_artist.xycoords=info_artist.boxcoords=ax.transAxes
                info_artist.xy=info_artist.xybox=(place[0],place[1]+size[1])
            fig.canvas.draw()
            b=info_artist.get_window_extent(renderer).transformed(ax.transAxes.inverted())
            occupied=[(b.x0,b.y0,b.x1,b.y1)]
            b=legend.get_window_extent(renderer)
            size=(b.width/ax.bbox.width,b.height/ax.bbox.height)
            place=clear_box(a,(ax.get_xlim(),ax.get_ylim()),size,(.025 if xlim is not None else .36,.965-size[1]),occupied)
            if place is not None:
                legend.set_bbox_to_anchor((place[0],place[1]+size[1]))
            fig.canvas.draw()
        if xlim is not None and px is not None:
            renderer=fig.canvas.get_renderer()
            def norm_rect(item):
                b=item.get_window_extent(renderer).transformed(ax.transAxes.inverted())
                return b.x0,b.y0,b.x1,b.y1
            bb=peak_text.get_window_extent(renderer)
            size=(bb.width/ax.bbox.width,bb.height/ax.bbox.height)
            preferred=(.62,.68) if not peak_visible else ((px-xlim[0])/(xlim[1]-xlim[0])+.02,peak/ax.get_ylim()[1]+.04)
            place=clear_box(a,(ax.get_xlim(),ax.get_ylim()),size,preferred,[norm_rect(info_artist),norm_rect(legend)])
            if place is not None:
                if peak_visible:
                    peak_text.xycoords=ax.transAxes
                    peak_text.set_anncoords(ax.transAxes)
                else: peak_text.set_transform(ax.transAxes)
                peak_text.set_position(place)
            else:
                peak_text.set_visible(False)
                fig.text(.08,.015,f'峰值应力 {peak:.3f} MPa'+('（峰值位于显示范围外）' if not peak_visible else ''),fontsize=9)
            fig.canvas.draw()
        if result_artist is not None:
            renderer=fig.canvas.get_renderer()
            def rectangle(artist):
                bb=artist.get_window_extent(renderer).transformed(ax.transAxes.inverted())
                return bb.x0,bb.y0,bb.x1,bb.y1
            occupied=[rectangle(info_artist),rectangle(legend)]
            if px is not None: occupied.append(rectangle(peak_text))
            bb=rectangle(result_artist)
            size=(bb[2]-bb[0],bb[3]-bb[1])
            cy=(center-ax.get_ylim()[0])/(ax.get_ylim()[1]-ax.get_ylim()[0])
            preferred=(.025,.065) if xlim is not None else (.51,cy-size[1]/2)
            location=clear_box(a,(ax.get_xlim(),ax.get_ylim()),size,preferred,occupied)
            if location is None:
                # Guaranteed separate area if the data fill all usable in-plot space.
                pos=ax.get_position()
                ax.set_position([pos.x0,pos.y0+.13,pos.width,pos.height-.13])
                result_artist.xycoords=fig.transFigure
                result_artist.boxcoords=fig.transFigure
                result_artist.xy=result_artist.xybox=(.45,.015)
            else:
                result_artist.xycoords=ax.transAxes
                result_artist.boxcoords=ax.transAxes
                result_artist.xy=result_artist.xybox=location
                occupied.append((*location,location[0]+size[0],location[1]+size[1]))
            band_text.set_transform(ax.transAxes)
            bb=band_text.get_window_extent(renderer)
            size=(bb.width/ax.bbox.width,bb.height/ax.bbox.height)
            location=clear_box(a,(ax.get_xlim(),ax.get_ylim()),size,(.30,cy-size[1]/2),occupied)
            if location is None:
                band_text.set_transform(fig.transFigure)
                band_text.set_position((.08,.025))
            else: band_text.set_position(location)
            fig.canvas.draw()
        for tick,line in zip(ax.get_xticks(),ax.get_xgridlines()):
            if np.isclose(tick,0,atol=1e-12):
                line.set_visible(False)
        fig.savefig(path,dpi=600)
        return fig
